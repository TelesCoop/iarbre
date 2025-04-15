from django.core.management import BaseCommand
import rasterio
from rasterio import features
import numpy as np
from iarbre_data.data_config import FACTORS
from iarbre_data.settings import BASE_DIR

from iarbre_data.utils.database import log_progress, select_city
from typing import Dict, Any
from plantability.constants import colors, rgb_colors


def compute_weighted_sum(
    raster_directory: str,
    output_file: str,
    meta: Dict[str, Any],
    result: np.ndarray,
    factor_name: str,
    weight: float,
) -> None:
    """
    Compute the weighted sum of raster data and save the result to a file.

    Args:
        raster_directory (str): The directory containing the raster files.
        output_file (str): The path to the output file where the result will be saved.
        meta (Dict[str, Any]): Metadata for the output raster file.
        result (np.ndarray): The array to store the computed weighted sum.
        factor_name (str): The name of the factor to process.
        weight (float): The weight to apply to the factor data.

    Returns:
        None
    """
    factor_file = raster_directory + factor_name + ".tif"
    log_progress(
        f"Processing: {factor_file.split('/')[-1].split('.')[0]} with weight {weight}"
    )

    with rasterio.open(factor_file) as src:
        factor_data = src.read(1).astype(np.float32)
        result += weight * factor_data / 100
    del factor_data

    meta.update(dtype=np.float32, count=1, compress="lzw", nodata=-9999)
    with rasterio.open(output_file, "w", **meta) as dst:
        dst.write(result.astype(np.float32), 1)

    log_progress(f"Weighted sum written to {output_file}")


def cut_outside_cities(
    meta: Dict[str, Any], result: np.ndarray, all_cities_union: Any
) -> np.ndarray:
    """
    Cut everything outside the cities and set nodata values for areas outside the cities.

    Args:
        meta (Dict[str, Any]): Metadata for the output raster file.
        result (np.ndarray): The array to store the computed weighted sum.
        all_cities_union (Any): The union of all city geometries.

    Returns:
        np.ndarray: The updated result array with nodata values outside the cities.
    """
    shape = result.shape
    mask = features.geometry_mask(
        [all_cities_union],
        out_shape=shape,
        transform=meta["transform"],
        all_touched=True,
        invert=True,
    )
    nodata_value = meta.get("nodata", -9999)
    result = np.where(mask, result, nodata_value)
    return result


def threshold_and_convert_to_colors(
    result: np.ndarray, rgb_colors: Dict[float, np.ndarray], colors: Dict[float, str]
) -> np.ndarray:
    """
    Apply thresholding to the result array and convert it to RGB colors.

    Args:
        result (np.ndarray): The array containing the computed weighted sum.
        rgb_colors (Dict[float, np.ndarray]): A dictionary mapping threshold values to RGB color arrays.
        colors (Dict[float, str]): A dictionary mapping threshold values to color names.

    Returns:
        np.ndarray: The array with RGB color values.
    """
    thresholds = sorted(colors.keys())
    result_colors = np.zeros(result.shape + (3,), dtype=np.uint8)  # RGB output

    # Apply thresholds and convert to colors
    mask = result <= thresholds[0]
    result_colors[mask] = rgb_colors[thresholds[0]]

    for i in range(0, len(thresholds) - 1):
        lower = thresholds[i]
        upper = thresholds[i + 1]
        mask = (result > lower) & (result <= upper)
        result_colors[mask] = rgb_colors[upper]

    mask = result > thresholds[-1]
    result_colors[mask] = rgb_colors[thresholds[-1]]
    nodata_mask = result == -9999
    result_colors[nodata_mask] = np.array([255, 255, 255], dtype=np.uint8)

    return result_colors


class Command(BaseCommand):
    help = "Compute and save factors data."

    def handle(self, *args, **options):
        """Compute and save factor data for the selected city."""
        raster_directory = str(BASE_DIR) + "/media/rasters/"
        output_file = str(BASE_DIR) + "/media/rasters/plantability.tif"
        output_color_file = str(BASE_DIR) + "/media/rasters/plantability_colors.tif"

        # Init raster
        file_path = raster_directory + list(FACTORS.keys())[0] + ".tif"
        with rasterio.open(file_path) as ref_src:
            meta = ref_src.meta.copy()
            shape = ref_src.shape

        result = np.zeros(shape, dtype=np.float32)

        for factor_name, weight in FACTORS.items():
            compute_weighted_sum(
                raster_directory, output_file, meta, result, factor_name, weight
            )

        # Cut everything outside cities
        all_cities = select_city(None).union_all()
        result = cut_outside_cities(meta, result, all_cities)

        with rasterio.open(output_file, "w", **meta) as dst:
            dst.write(result, 1)

        # Convert to RGB and colors
        result_colors = threshold_and_convert_to_colors(result, rgb_colors, colors)

        color_meta = meta.copy()
        color_meta.update(dtype=rasterio.uint8, count=3, nodata=None)

        with rasterio.open(output_color_file, "w", **color_meta) as dst:
            for i in range(3):  # Write each RGB channel
                dst.write(result_colors[:, :, i], i + 1)
