import rasterio
from django.contrib.gis.geos import GEOSGeometry

from django.core.management import BaseCommand
from django.db import transaction
from shapely.geometry import box
from shapely.ops import transform
import pyproj
import itertools
from tqdm import tqdm

from iarbre_data.models import Tile, City, Iris
from iarbre_data.settings import TARGET_MAP_PROJ, BASE_DIR
from typing import Optional, Tuple, Type
from django.db.models import Model
from shapely.geometry.base import BaseGeometry

from plantability.constants import score_thresholding

BATCH_SIZE = 50_000


def get_administrative_attachment(
    polygon: BaseGeometry, previous: Optional[Model], model: Type[Model]
) -> Tuple[Optional[int], Optional[Model]]:
    """
    Determine the administrative attachment (e.g., city or IRIS) for a given polygon.

    Parameters:
    -----------
    polygon : shapely.geometry.base.BaseGeometry
        The polygon for which to determine the administrative attachment.
    previous : Optional[Model]
        The previous administrative unit (e.g., city or IRIS). If provided, the function first checks
        if the polygon intersects with this unit.
    model : Type[Model]
        The Django model to query for administrative units (e.g., City or Iris).

    Returns:
    --------
    Tuple[Optional[int], Optional[Model]]
        A tuple containing:
        - The ID of the administrative unit that intersects with the polygon, or None if no match is found.
        - The administrative unit (e.g., city or IRIS) that intersects with the polygon, or None if no match is found.
    """
    if previous is not None and previous.geometry.intersects(GEOSGeometry(polygon.wkt)):
        attachment_id = previous.id
    else:
        qs = model.objects.filter(geometry__intersects=GEOSGeometry(polygon.wkt))
        if qs:
            previous = qs[0]
            attachment_id = previous.id
        else:
            attachment_id = None
    return attachment_id, previous


def raster_to_db_tiles(raster_path: str, batch_size: int = BATCH_SIZE) -> None:
    """
    Convert a raster file to Tile objects in the database.
    Each pixel becomes a square polygon with plantability indices based on the pixel value.

    Parameters:
    -----------
    raster_path : str
        Path to the input raster file.
    batch_size : int, optional
        Number of tiles to create before committing to the database. Default is BATCH_SIZE.
    """

    with rasterio.open(raster_path) as src:
        data = src.read(1)

        transform_raster = src.transform
        crs = src.crs
        project = pyproj.Transformer.from_crs(
            crs, TARGET_MAP_PROJ, always_xy=True
        ).transform

        tiles = []
        tile_count = 0
        total_tiles = 0
        previous_iris = None
        previous_city = None
        total_pixels = data.shape[0] * data.shape[1]
        for row_idx, col_idx in tqdm(
            itertools.product(range(data.shape[0]), range(data.shape[1])),
            total=total_pixels,
            desc="Processing pixels",
        ):
            value = data[row_idx, col_idx]
            # Outside the cities they are nodata
            if value == src.nodata:
                continue

            x_min, y_max = transform_raster * (col_idx, row_idx)
            x_max, y_min = transform_raster * (col_idx + 1, row_idx + 1)
            polygon = box(x_min, y_min, x_max, y_max)

            # update or not admin attachment
            iris_id, previous_iris = get_administrative_attachment(
                polygon, previous_iris, Iris
            )
            city_id, previous_city = get_administrative_attachment(
                polygon, previous_city, City
            )

            plantability_indice = float(value)
            plantability_normalized_indice = score_thresholding(plantability_indice)

            # Create Tile object
            tile = Tile(
                geometry=GEOSGeometry(polygon.wkt),
                map_geometry=GEOSGeometry(transform(project, polygon).wkt),
                plantability_indice=plantability_indice,
                plantability_normalized_indice=plantability_normalized_indice,
                city_id=city_id,
                iris_id=iris_id,
            )
            tiles.append(tile)
            tile_count += 1
            total_tiles += 1

            # Avoid OOM errors by committing in batches
            if tile_count % batch_size == 0:
                with transaction.atomic():
                    Tile.objects.bulk_create(tiles, batch_size=batch_size)
                tiles.clear()
                tile_count = 0
        # Save last batch if any remain
        if tiles:
            Tile.objects.bulk_create(tiles, batch_size=batch_size)


class Command(BaseCommand):
    help = "Compute and save factors data."

    def handle(self, *args, **options):
        raster_file = str(BASE_DIR) + "/media/rasters/plantability.tif"
        raster_to_db_tiles(raster_file)
