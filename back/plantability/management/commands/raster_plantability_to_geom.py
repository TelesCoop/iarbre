import itertools

import rasterio
from django.contrib.gis.geos import GEOSGeometry
from tqdm import tqdm

from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import Model
import pyproj
from shapely.geometry import box
from shapely.ops import transform
from shapely.geometry.base import BaseGeometry
from concurrent.futures import ProcessPoolExecutor

from iarbre_data.models import Tile, City, Iris
from iarbre_data.settings import TARGET_MAP_PROJ, BASE_DIR
from iarbre_data.utils.database import log_progress

from typing import Optional, Tuple, Type, List


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


def process_raster_chunk(args) -> List[dict]:
    chunk_data, row_start, transform_raster, nodata, crs = args

    tile_dicts = []
    project = pyproj.Transformer.from_crs(
        crs, TARGET_MAP_PROJ, always_xy=True
    ).transform
    previous_iris = None
    previous_city = None

    for row_idx, col_idx in itertools.product(
        range(chunk_data.shape[0]), range(chunk_data.shape[1])
    ):
        value = chunk_data[row_idx, col_idx]
        if value == nodata:
            continue

        x_min, y_max = transform_raster * (col_idx, row_start + row_idx)
        x_max, y_min = transform_raster * (col_idx + 1, row_start + row_idx + 1)
        polygon = box(x_min, y_min, x_max, y_max)
        iris_id, previous_iris = get_administrative_attachment(
            polygon, previous_iris, Iris
        )
        city_id, previous_city = get_administrative_attachment(
            polygon, previous_city, City
        )

        tile_dicts.append(
            {
                "geometry": polygon,
                "map_geometry": transform(project, polygon),
                "plantability_indice": float(value),
                "plantability_normalized_indice": normalize_plantability(value),
                "city_id": city_id,
                "iris_id": iris_id,
            }
        )

    return tile_dicts


def raster_to_db_tiles(
    raster_path: str, batch_size: int = BATCH_SIZE, n_threads: int = 4
) -> None:
    with rasterio.open(raster_path) as src:
        data = src.read(1)
        transform_raster = src.transform
        crs = src.crs
        nodata = src.nodata

        height = data.shape[0]
        chunk_size = height // n_threads or 1

        chunks = [
            (data[i : i + chunk_size], i, transform_raster, nodata, crs)
            for i in range(0, height, chunk_size)
        ]

        buffer = []
        total_tiles = 0
        with ProcessPoolExecutor(max_workers=n_threads) as executor:
            for tile_dicts in tqdm(
                executor.map(process_raster_chunk, chunks),
                total=len(chunks),
                desc="Processing raster chunks",
            ):
                for d in tile_dicts:
                    buffer.append(Tile(**d))
                    if len(buffer) >= batch_size:
                        with transaction.atomic():
                            Tile.objects.bulk_create(buffer, batch_size=batch_size)
                        total_tiles += len(buffer)
                        log_progress(f"Inserted {total_tiles} tiles")
                        buffer.clear()

        if buffer:
            with transaction.atomic():
                Tile.objects.bulk_create(buffer, batch_size=batch_size)
            total_tiles += len(buffer)
            log_progress(f"Inserted final batch of {len(buffer)} tiles")


class Command(BaseCommand):
    help = "Convert plantatility data and save them in DB."

    def add_arguments(self, parser):
        """Add arguments to the command."""
        parser.add_argument(
            "--n_threads",
            type=int,
            default=6,
            help="Number of threads to use for generating tiles",
        )

    def handle(self, *args, **options):
        n_threads = options["n_threads"]
        raster_file = str(BASE_DIR) + "/media/rasters/plantability.tif"
        raster_to_db_tiles(raster_file, n_threads)
