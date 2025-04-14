from django.contrib.gis.db.models import Union
import rasterio
from django.core.management import BaseCommand
from rasterio.transform import from_origin
from rasterio.features import rasterize
import numpy as np
import os

from iarbre_data.data_config import FACTORS
from iarbre_data.models import City, Data
from iarbre_data.utils.database import load_geodataframe_from_db, log_progress


def rasterize_data_across_all_cities(
    factor_name, height, width, transform, output_dir=None
):
    """
    Convert Data polygons to a single binary raster across all cities to avoid border effects.

    Args:
        factor_name (str): Name of the factor to transform to raster
        output_dir (str): Directory to save the raster file

    Returns:
        str: Path to the generated raster file
    """

    os.makedirs(output_dir, exist_ok=True)
    qs = Data.objects.filter(factor=factor_name)
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
    # Save the raster to file
    output_path = os.path.join(output_dir, f"{factor_name}.tif")
    log_progress(f"Saving {factor_name}")
    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=raster.dtype,
        crs="EPSG:2154",
        transform=transform,
    ) as dst:
        dst.write(raster, 1)


class Command(BaseCommand):
    help = "Convert Data polygons to raster."

    def handle(self, *args, **options):
        output_dir = "/home/ludo/rasters"
        resolution = 1
        all_cities_union = City.objects.aggregate(union=Union("geometry"))["union"]

        # Get the bounds of the combined city geometries
        minx, miny, maxx, maxy = all_cities_union.extent

        # Calculate raster dimensions
        width = int((maxx - minx) / resolution)
        height = int((maxy - miny) / resolution)

        # Create transformation for the output raster
        transform = from_origin(minx, maxy, resolution, resolution)
        for factor_name in FACTORS.keys():
            log_progress(f"Processing {factor_name}")
            rasterize_data_across_all_cities(
                factor_name, height, width, transform, output_dir=output_dir
            )
