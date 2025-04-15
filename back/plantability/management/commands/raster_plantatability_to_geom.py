import rasterio

from django.core.management import BaseCommand
from django.db import transaction
from shapely.geometry import box
from shapely.ops import transform
import pyproj

from iarbre_data.models import Tile, City, Iris
from iarbre_data.settings import TARGET_MAP_PROJ, BASE_DIR
from iarbre_data.utils.database import log_progress
from typing import Optional, Tuple, Type
from django.db.models import Model
from shapely.geometry.base import BaseGeometry

BATCH_SIZE = 10_000


def normalize_plantability(value: float) -> float:
    """
    Convert raw plantability value to normalized index based on thresholds.

    This function takes a raw plantability value and normalizes it to a predefined index
    based on specific thresholds. The normalization is done using a series of conditional
    checks to map the raw value to a normalized index.

    Parameters:
    -----------
    value : float
        The raw plantability value to be normalized.

    Returns:
    --------
    float
        The normalized plantability index.
    """
    if value < -5:
        normalized_value = 0.0
    elif value < -2:
        normalized_value = 2
    elif value < -0.75:
        normalized_value = 4
    elif value < 0.15:
        normalized_value = 6
    elif value < 2.5:
        normalized_value = 8
    else:
        normalized_value = 10
    return normalized_value


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
    if previous is not None and previous.geometry.intersects(polygon):
        attachment_id = previous.id
    else:
        qs = model.objects.filter(geometry__intersects=polygon)
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
        for row_idx in range(data.shape[0]):
            for col_idx in range(data.shape[1]):
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
                plantability_normalized_indice = normalize_plantability(
                    plantability_indice
                )

                # Create Tile object
                tile = Tile(
                    geometry=polygon,
                    map_geometry=transform(project, polygon),
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
                    log_progress(
                        f"Processed {total_tiles} tiles ({tile_count} in last batch)"
                    )
                    tiles.clear()
                    tile_count = 0

                # Save last batch if any remain
            if tiles:
                Tile.objects.bulk_create(tiles, batch_size=batch_size)
                log_progress(f"Processed final batch of {len(tiles)} tiles")


class Command(BaseCommand):
    help = "Compute and save factors data."

    def handle(self, *args, **options):
        raster_file = BASE_DIR + "/media/rasters/plantability_colors.tif"
        raster_to_db_tiles(raster_file)
