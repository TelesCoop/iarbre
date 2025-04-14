from django.core.management import BaseCommand
import rasterio
import numpy as np
from iarbre_data.data_config import FACTORS
from iarbre_data.utils.database import log_progress
from typing import Dict, Any


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
    log_progress(f"Processing: {factor_file} with weight {weight}")

    with rasterio.open(factor_file) as src:
        factor_data = src.read(1)
        result += weight * factor_data / 100
    del factor_data

    meta.update(dtype=np.float32, count=1, compress="lzw", nodata=0)
    with rasterio.open(output_file, "w", **meta) as dst:
        dst.write(result.astype(np.float32), 1)

    log_progress(f"Weighted sum written to {output_file}")


class Command(BaseCommand):
    help = "Compute and save factors data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete already existing TileFactor.",
        )

    def handle(self, *args, **options):
        """Compute and save factor data for the selected city."""
        raster_directory = "/home/ludo/rasters/"  # Update this path
        output_file = "/home/ludo/rasters/weighted_sum.tif"

        # Init raster
        file_path = raster_directory + list(FACTORS.keys())[0] + ".tif"

        with rasterio.open(file_path) as ref_src:
            meta = ref_src.meta.copy()
            shape = ref_src.shape

        # Initialize results raster with zeros
        result = np.zeros(shape, dtype=np.float32)

        for factor_name, weight in FACTORS.items():
            compute_weighted_sum(
                raster_directory, output_file, meta, result, factor_name, weight
            )
