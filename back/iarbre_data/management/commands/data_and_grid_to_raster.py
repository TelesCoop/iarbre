from django.contrib.gis.db.models import Union
import rasterio
from django.core.management import BaseCommand
from rasterio.transform import from_origin
from rasterio.features import rasterize
import numpy as np
import os
import geopandas as gpd

from scipy import ndimage

from iarbre_data.data_config import FACTORS
from iarbre_data.models import City, Data
from iarbre_data.settings import BASE_DIR
from iarbre_data.utils.database import load_geodataframe_from_db, log_progress


def rasterize_data_across_all_cities(
    factor_name: str,
    height: int,
    width: int,
    height_out: int,
    width_out: int,
    transform: rasterio.Affine,
    transform_out: rasterio.Affine,
    all_cities_union: gpd.GeoDataFrame,
    grid_size: int = 5,
    output_dir: str = None,
) -> None:
    """
    Convert Data polygons to a single binary raster across all cities to avoid border effects.

    This function rasterizes the geometries of a specified factor across all cities, applies a convolution
    to aggregate the raster values into larger blocks, and saves the resulting raster to a file.

    Args:
        factor_name (str): Name of the factor to transform to raster.
        height (int): Height of the output raster.
        width (int): Width of the output raster.
        height_out (int): Height of the output raster after convolution.
        width_out (int): Width of the output raster after convolution.
        transform (rasterio.Affine): Affine transformation for the factor transformation.
        transform_out (rasterio.Affine): Affine transformation for the raster output.
        all_cities_union (gpd.GeoDataFrame): GeoDataFrame containing the union of all city geometries.
        grid_size (int, optional): Size of the convolution kernel. Defaults to 5.
        output_dir (str, optional): Directory to save the raster file. Defaults to None.

    Returns:
        None
    """
    max_count = grid_size * grid_size
    os.makedirs(output_dir, exist_ok=True)

    qs = Data.objects.filter(factor=factor_name, geometry__intersects=all_cities_union)
    factor_df = load_geodataframe_from_db(qs, [])
    log_progress(f"Rasterizing {factor_name}")
    # Rasterize the shapes
    raster = rasterize(
        factor_df.geometry,
        out_shape=(height, width),
        transform=transform,
        fill=0,
        default_value=1,
        dtype=np.uint8,
    )
    if len(raster[raster > 0]) == 0:
        raise ValueError(f"{factor_name} is producing a blank tif.")
    log_progress("Summing on 5x5")
    kernel = np.ones((grid_size, grid_size))
    coarse_raster = ndimage.convolve(raster, kernel, mode="constant", cval=0)[
        0 : height_out * grid_size : grid_size,
        0 : width_out * grid_size : grid_size,
    ]
    coarse_raster = (coarse_raster / max_count * 100).astype(np.int8)
    # Save the raster to file
    output_path = os.path.join(output_dir, f"{factor_name}.tif")
    log_progress(f"Saving {factor_name}")
    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=height_out,
        width=width_out,
        count=1,
        dtype=raster.dtype,
        crs="EPSG:2154",
        transform=transform_out,
    ) as dst:
        dst.write(coarse_raster, 1)


class Command(BaseCommand):
    help = "Convert Data polygons to raster."

    def add_arguments(self, parser):
        """Add arguments to the command."""
        parser.add_argument(
            "--grid-size", type=int, default=5, help="Grid size in meters"
        )

    def handle(self, *args, **options):
        output_dir = str(BASE_DIR) + "/media/rasters/"
        resolution = 1
        grid_size = options["grid_size"]
        all_cities_union = City.objects.aggregate(union=Union("geometry"))["union"]
        minx, miny, maxx, maxy = all_cities_union.extent

        width = int((maxx - minx) / resolution)
        height = int((maxy - miny) / resolution)
        transform = from_origin(minx, maxy, resolution, resolution)

        width_out = int((maxx - minx) / grid_size)
        height_out = int((maxy - miny) / grid_size)
        transform_out = from_origin(minx, maxy, grid_size, grid_size)

        for factor_name in FACTORS.keys():
            log_progress(f"Processing {factor_name}")
            rasterize_data_across_all_cities(
                factor_name,
                height,
                width,
                height_out,
                width_out,
                transform,
                transform_out,
                all_cities_union=all_cities_union,
                grid_size=grid_size,
                output_dir=output_dir,
            )
