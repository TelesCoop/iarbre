import rasterio
from rasterio.windows import Window
from django.core.management import BaseCommand
from django.contrib.gis.db.models import Extent
from typing import List, Iterator

from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import json
from typing import Dict

from iarbre_data.models import Tile
from iarbre_data.settings import BASE_DIR
from iarbre_data.utils.database import log_progress
from iarbre_data.data_config import META_FACTORS_MAPPING

BATCH_SIZE = 5_000


def get_tile_batches(batch_size: int) -> Iterator[List[Tile]]:
    """
    Yields batches of tiles from the database without loading all tiles into memory.

    Parameters:
    -----------
    batch_size : int
        Number of tiles to include in each batch.

    Yields:
    -------
    List[Tile]
        A batch of tiles.
    """
    last_id = 0
    while True:
        # https://docs.djangoproject.com/en/5.2/ref/models/querysets/#gt
        batch = Tile.objects.filter(id__gt=last_id).order_by("id")[:batch_size]
        if not batch:
            break
        yield batch
        last_id = list(batch)[-1].id


def compute_meta_factors(land_uses: Dict[str, float]) -> Dict[str, float]:
    """
    Compute meta-factors for a given set of land uses.

    Parameters:
    -----------
    land_uses : Dict[str, float]
        A dictionary where keys are land use types and values are their corresponding scores.

    Returns:
    --------
    Dict[str, float]
        A dictionary where keys are meta-categories and values are the computed scores for those categories.
    """
    meta_factors = {}
    for meta_category, factors in META_FACTORS_MAPPING.items():
        total_score = 0
        for factor in factors:
            score = land_uses.get(factor, 0)
            total_score += score
        meta_factors[meta_category] = round(total_score, 2)

    return meta_factors


def process_tile_batch(
    tiles: List[Tile], raster_files: List[str], raster_path: str
) -> None:
    """
    Process a batch of tiles against all raster files and update their details and meta_factors fields.

    Parameters:
    -----------
    tiles : List[Tile]
        List of tiles to process.
    raster_files : List[str]
        List of raster file names to process.
    raster_path : str
        Path to the directory containing raster files.
    """
    tile_land_use = {tile.id: {} for tile in tiles}
    min_x, min_y, max_x, max_y = tiles.aggregate(Extent("geometry"))["geometry__extent"]

    for raster_file in raster_files:
        raster_file_path = os.path.join(raster_path, raster_file)
        land_use_type = os.path.splitext(raster_file)[0]
        log_progress(f"Processing {land_use_type}")

        with rasterio.open(raster_file_path) as src:
            top, left = src.index(min_x, max_y)
            bottom, right = src.index(max_x, min_y)
            top = max(0, top)
            bottom = min(src.height, bottom)
            left = max(0, left)
            right = min(src.width, right)
            # Read the data only within the window
            window = Window.from_slices((top, bottom), (left, right))
            data = src.read(1, window=window)
            for tile in tiles:
                x, y = tile.geometry.centroid.x, tile.geometry.centroid.y
                row, col = src.index(x, y)
                if 0 <= row < src.height and 0 <= col < src.width:
                    # Adjust row and col to the window's coordinate system
                    row -= window.row_off
                    col -= window.col_off
                    if 0 <= row < window.height and 0 <= col < window.width:
                        pixel_value = float(data[row, col])
                        if pixel_value > 0:
                            tile_land_use[tile.id][land_use_type] = pixel_value

    log_progress("Top 5 land use and meta-factors.")
    tiles_to_update = []
    for tile in tiles:
        land_uses = tile_land_use[tile.id].copy()
        reseaux_souterrains_total = 0
        keys_to_remove = []
        for key in land_uses:
            if key in META_FACTORS_MAPPING["Réseaux et infrastructures"]:
                reseaux_souterrains_total += land_uses[key]
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del land_uses[key]

        if reseaux_souterrains_total > 0:
            land_uses["Réseaux et infrastructures"] = reseaux_souterrains_total

        meta_factors = compute_meta_factors(land_uses)
        sorted_land_uses = sorted(
            land_uses.items(), key=lambda item: item[1], reverse=True
        )
        top5_land_use = dict(sorted_land_uses[:5])

        details = json.loads(tile.details) if tile.details else {}
        details["top5_land_use"] = top5_land_use
        tile.details = json.dumps(details)

        meta_factors_field = json.loads(tile.meta_factors) if tile.meta_factors else {}
        meta_factors_field["meta_factors"] = meta_factors
        tile.meta_factors = json.dumps(meta_factors_field)
        tiles_to_update.append(tile)
    log_progress("Bulk update in the DB.")
    Tile.objects.bulk_update(
        tiles_to_update, ["details", "meta_factors"], batch_size=1000
    )


def raster_to_top5_land_use(raster_path: str, batch_size: int = BATCH_SIZE) -> None:
    """
    Using raster files of land use, pick the top 5 and save them as JSON in the `details` field in the Tile model.
    Land use is described by the values of the pixels in raster, between 0 (not present) and 100 (100% of the surface).

    Parameters:
    -----------
    raster_path : str
        Path to the input raster files (30 factors).
    batch_size : int, optional
        Number of tiles to update in a batch. Default is BATCH_SIZE.
    """
    raster_files = [
        f
        for f in os.listdir(raster_path)
        if f.endswith(".tif") and "plantability" not in f
    ]
    log_progress(f"Found {len(raster_files)} raster files to process")
    total_tiles = Tile.objects.count()
    log_progress(f"Processing {total_tiles} tiles in batches of {batch_size}")

    batch_count = (total_tiles + batch_size - 1) // batch_size

    with ThreadPoolExecutor(max_workers=6) as executor:
        future_to_batch = {
            executor.submit(
                process_tile_batch,
                tiles=tile_batch,
                raster_files=raster_files,
                raster_path=raster_path,
            ): i
            for i, tile_batch in enumerate(get_tile_batches(batch_size))
        }

        for future in as_completed(future_to_batch):
            batch_index = future_to_batch.pop(future)
            future.result()
            log_progress(f"Completed batch {batch_index + 1} of {batch_count}")
    log_progress("Successfully processed all tiles")


class Command(BaseCommand):
    help = "Process raster files to extract top 5 land use types for each tile"

    def add_arguments(self, parser):
        parser.add_argument(
            "--raster_path",
            type=str,
            default=str(BASE_DIR) + "/media/rasters/",
            help="Path to the directory containing raster files",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=BATCH_SIZE,
            help="Number of tiles to process in each batch",
        )

    def handle(self, *args, **options):
        raster_path = options["raster_path"]
        batch_size = options["batch_size"]
        raster_to_top5_land_use(raster_path, batch_size)
