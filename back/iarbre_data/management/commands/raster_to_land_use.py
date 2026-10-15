import rasterio
from rasterio.transform import rowcol
from rasterio.windows import Window
from django.core.management import BaseCommand
from django.contrib.gis.db.models import Extent
from django.db import connection
from django.db.models import Max, Min
from typing import List, Iterator, Tuple

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import os
import json
import numpy as np
from typing import Dict

from iarbre_data.models import Tile
from iarbre_data.settings import BASE_DIR
from iarbre_data.utils.database import log_progress
from iarbre_data.data_config import FACTORS, META_FACTORS_MAPPING

BATCH_SIZE = 5_000


def get_batch_bounds(batch_size: int) -> Iterator[Tuple[int, int]]:
    """
    Yields (first_id, last_id) of consecutive batches of tiles, ordered by id.
    Only ids are passed to workers, which fetch their own tiles.

    Parameters:
    -----------
    batch_size : int
        Number of tiles to include in each batch.

    Yields:
    -------
    Tuple[int, int]
        First and last tile id of a batch (inclusive).
    """
    last_id = 0
    while True:
        # https://docs.djangoproject.com/en/5.2/ref/models/querysets/#gt
        bounds = (
            Tile.objects.filter(id__gt=last_id)
            .order_by("id")[:batch_size]
            .aggregate(first=Min("id"), last=Max("id"))
        )
        if bounds["first"] is None:
            break
        yield bounds["first"], bounds["last"]
        last_id = bounds["last"]


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

    # Centroids are computed once, then looked up in every raster with numpy
    tile_ids = [tile.id for tile in tiles]
    centroids = [tile.geometry.centroid for tile in tiles]
    xs = np.fromiter((c.x for c in centroids), float, len(centroids))
    ys = np.fromiter((c.y for c in centroids), float, len(centroids))

    for raster_file in raster_files:
        raster_file_path = os.path.join(raster_path, raster_file)
        land_use_type = os.path.splitext(raster_file)[0]

        with rasterio.open(raster_file_path) as src:
            top, left = src.index(min_x, max_y)
            bottom, right = src.index(max_x, min_y)
            top = max(0, top)
            bottom = min(src.height, bottom)
            left = max(0, left)
            right = min(src.width, right)
            if bottom <= top or right <= left:
                continue
            # Read the data only within the window
            window = Window.from_slices((top, bottom), (left, right))
            data = src.read(1, window=window)
            # Same as src.index, which does not accept arrays
            rows, cols = (np.asarray(a) for a in rowcol(src.transform, xs, ys))
            # Adjust rows and cols to the window's coordinate system
            rows -= window.row_off
            cols -= window.col_off
            in_window = (
                (rows >= 0) & (rows < window.height) & (cols >= 0) & (cols < window.width)
            )
            pixel_values = np.zeros(len(tile_ids))
            pixel_values[in_window] = data[rows[in_window], cols[in_window]]
            for i in np.flatnonzero(pixel_values > 0):
                tile_land_use[tile_ids[i]][land_use_type] = float(pixel_values[i])

    tiles_to_update = []
    for tile in tiles:
        land_uses_raw = tile_land_use[tile.id].copy()

        meta_factors = compute_meta_factors(land_uses_raw)

        # Aggregate individual network factors into "Réseaux et infrastructures"
        # because they are sensible data
        land_uses_aggregated = land_uses_raw.copy()
        reseaux_souterrains_total = 0
        keys_to_remove = []
        for key in land_uses_aggregated:
            if key in META_FACTORS_MAPPING["Réseaux et infrastructures"]:
                reseaux_souterrains_total += land_uses_aggregated[key]
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del land_uses_aggregated[key]

        if reseaux_souterrains_total > 0:
            land_uses_aggregated[
                "Réseaux et infrastructures"
            ] = reseaux_souterrains_total

        sorted_land_uses = sorted(
            land_uses_aggregated.items(), key=lambda item: item[1], reverse=True
        )
        top5_land_use = dict(sorted_land_uses[:5])

        details = json.loads(tile.details) if tile.details else {}
        details["top5_land_use"] = top5_land_use
        details["land_uses"] = land_uses_raw  # Save all for PCA analysis
        tile.details = json.dumps(details)

        meta_factors_field = json.loads(tile.meta_factors) if tile.meta_factors else {}
        meta_factors_field["meta_factors"] = meta_factors
        tile.meta_factors = json.dumps(meta_factors_field)
        tiles_to_update.append(tile)
    Tile.objects.bulk_update(
        tiles_to_update, ["details", "meta_factors"], batch_size=1000
    )


def process_batch_bounds(
    bounds: Tuple[int, int], raster_files: List[str], raster_path: str
) -> None:
    """Fetch the tiles between bounds (inclusive) and process them."""
    tiles = Tile.objects.filter(id__range=bounds).order_by("id")
    process_tile_batch(tiles, raster_files, raster_path)


def process_batch_bounds_in_thread(
    bounds: Tuple[int, int], raster_files: List[str], raster_path: str
) -> None:
    try:
        process_batch_bounds(bounds, raster_files, raster_path)
    finally:
        # Each thread has its own connection, do not leave it open
        connection.close()


def process_batches(
    batches: List[Tuple[int, int]],
    raster_files: List[str],
    raster_path: str,
    number_of_threads: int,
) -> int:
    """Process several batches in a worker, using a pool of threads."""
    if number_of_threads == 1:
        for bounds in batches:
            process_batch_bounds(bounds, raster_files, raster_path)
    else:
        with ThreadPoolExecutor(max_workers=number_of_threads) as executor:
            futures = [
                executor.submit(
                    process_batch_bounds_in_thread, bounds, raster_files, raster_path
                )
                for bounds in batches
            ]
            for future in as_completed(futures):
                future.result()
    return len(batches)


def raster_to_top5_land_use(
    raster_path: str,
    batch_size: int = BATCH_SIZE,
    number_of_workers: int = 1,
    number_of_threads_by_worker: int = 1,
) -> None:
    """
    Using raster files of land use, pick the top 5 and save them as JSON in the `details` field in the Tile model.
    Land use is described by the values of the pixels in raster, between 0 (not present) and 100 (100% of the surface).

    Parameters:
    -----------
    raster_path : str
        Path to the input raster files (30 factors).
    batch_size : int, optional
        Number of tiles to update in a batch. Default is BATCH_SIZE.
    number_of_workers : int, optional
        Number of processes.
    number_of_threads_by_worker : int, optional
        Number of threads in each process.
    """
    raster_files = [
        f
        for f in os.listdir(raster_path)
        if f.endswith(".tif") and os.path.splitext(f)[0] in FACTORS
    ]
    log_progress(f"Found {len(raster_files)} raster files to process")
    batches = list(get_batch_bounds(batch_size))
    log_progress(f"Processing {len(batches)} batches of {batch_size} tiles")

    # Each worker task gets one batch per thread
    tasks = [
        batches[i : i + number_of_threads_by_worker]
        for i in range(0, len(batches), number_of_threads_by_worker)
    ]
    progress = 0

    # Same as MVTGenerator: run in the main process for tests,
    # a child process would destroy the testing database on close
    if number_of_workers == 1:
        for task in tasks:
            progress += process_batches(
                task, raster_files, raster_path, number_of_threads_by_worker
            )
            log_progress(f"Completed {progress} / {len(batches)} batches")
    else:
        with ProcessPoolExecutor(
            max_workers=number_of_workers,
            # avoid using same connexion as previous worker to avoid timeouts
            initializer=connection.close,
        ) as executor:
            futures = [
                executor.submit(
                    process_batches,
                    task,
                    raster_files,
                    raster_path,
                    number_of_threads_by_worker,
                )
                for task in tasks
            ]
            for future in as_completed(futures):
                progress += future.result()
                log_progress(f"Completed {progress} / {len(batches)} batches")
        connection.close()
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
        parser.add_argument(
            "--number_of_workers",
            "-nw",
            type=int,
            default=1,
            help="Number of processes",
        )
        parser.add_argument(
            "--number_of_threads_by_worker",
            "-ntw",
            type=int,
            default=1,
            help="Number of threads by process",
        )

    def handle(self, *args, **options):
        raster_to_top5_land_use(
            options["raster_path"],
            options["batch_size"],
            options["number_of_workers"],
            options["number_of_threads_by_worker"],
        )
