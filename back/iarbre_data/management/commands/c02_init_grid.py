"""Create a grid over the metropole or a selection of city and save it to DB"""
import gc
import itertools
import logging

import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.contrib.gis.geos import Polygon, GEOSGeometry
from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import Count
from tqdm import tqdm

from iarbre_data.management.commands.utils import select_city
from iarbre_data.models import Iris, Tile, City
from iarbre_data.settings import TARGET_PROJ, TARGET_MAP_PROJ


def create_squares_for_city(city, grid_size, logger, batch_size=int(1e6)) -> None:
    """
    Create square tiles for a specific city and save it to DB.

    Args:
        city (GeoPandas DataFrame): City GeoDataFrame.
        grid_size (int): The size of the grid in meters.
        logger (Logger): The logger object.
        batch_size (int): The size of the batch to save to the DB.

    Returns:
        None
    """
    city_id = city.id
    city_geom = city.geometry
    xmin, ymin, xmax, ymax = city_geom.bounds
    # Snap bounds to the nearest grid alignment so that all grids are aligned
    xmin = np.floor(xmin / grid_size) * grid_size
    ymin = np.floor(ymin / grid_size) * grid_size
    xmax = np.ceil(xmax / grid_size) * grid_size
    ymax = np.ceil(ymax / grid_size) * grid_size

    tiles = []
    for i, (x0, y0) in enumerate(
        tqdm(
            itertools.product(
                np.arange(xmin, xmax + grid_size, grid_size),
                np.arange(ymin, ymax + grid_size, grid_size),
            )
        )
    ):
        # Bounds
        x1 = x0 - grid_size
        y1 = y0 + grid_size

        number_of_decimals = 2  # centimeter-level precision
        x0, y0, x1, y1 = map(lambda v: round(v, number_of_decimals), (x0, y0, x1, y1))
        polygon = Polygon.from_bbox([x0, y0, x1, y1])
        polygon.srid = TARGET_PROJ
        iris_id = Iris.objects.filter(geometry__intersects=polygon)
        if len(iris_id) > 0:
            iris_id = iris_id[0].id
        else:
            iris_id = None
        # Init with -1 value
        tile = Tile(
            geometry=polygon,
            map_geometry=polygon.transform(TARGET_MAP_PROJ, clone=True),
            plantability_indice=0,
            plantability_normalized_indice=0.5,
            city_id=city_id,
            iris_id=iris_id,
        )
        tiles.append(tile)
        # Avoid OOM errors
        if (i + 1) % batch_size == 0:
            Tile.objects.bulk_create(tiles, batch_size=batch_size // 8)
            logger.info(f"Got {len(tiles)} tiles")
            tiles.clear()
            gc.collect()
    if tiles:  # Save last batch
        Tile.objects.bulk_create(tiles, batch_size=batch_size // 8)


def create_hexs_for_city(
    city,
    unit,
    a,
    logger,
    batch_size=int(1e6),
) -> None:
    """
    Create hexagonal tiles for a specific city.

    Args:
        city (City): The city object with geometry, ID, and name.
        unit (float): The size of the hexagon in meters.
        a (float): The ratio of the hexagon.
        logger (Logger): The logger object.
        batch_size (int): The size of the batch to save to the database.

    Returns:
        None
    """
    city_geom = city.geometry
    city_id = city.id
    xmin, ymin, xmax, ymax = city_geom.bounds
    hex_width = 3 * unit
    hex_height = 2 * unit * a
    xmin = hex_width * (np.floor(xmin / hex_width) - 1)
    ymin = hex_height * (np.floor(ymin / hex_height) - 1)
    xmax = hex_width * (np.ceil(xmax / hex_width) + 1)
    ymax = hex_height * (np.ceil(ymax / hex_height) + 1)

    cols = np.arange(xmin, xmax, 3 * unit)
    rows = np.arange(ymin / a, ymax / a, unit)
    tiles = []
    for x, (i, y) in tqdm(itertools.product(cols, enumerate(rows))):
        # Rows are not aligned
        offset = 1.5 * unit if i % 2 != 0 else 0
        x0 = x + offset
        dim = [
            (x0, y * a),
            (x0 + unit, y * a),
            (x0 + (1.5 * unit), (y + unit) * a),
            (x0 + unit, (y + (2 * unit)) * a),
            (x0, (y + (2 * unit)) * a),
            (x0 - (0.5 * unit), (y + unit) * a),
            (x0, y * a),
        ]
        # Optimize storage
        rounded_dim = [(round(x, 2), round(y, 2)) for (x, y) in dim]
        hexagon = Polygon(rounded_dim, srid=TARGET_PROJ)
        iris_id = Iris.objects.filter(geometry__intersects=hexagon)
        if len(iris_id) > 0:
            iris_id = iris_id[0].id
        else:
            iris_id = None
        tile = Tile(
            geometry=hexagon,
            map_geometry=hexagon.transform(TARGET_MAP_PROJ, clone=True),
            plantability_indice=0,
            plantability_normalized_indice=0.5,
            city_id=city_id,
            iris_id=iris_id,
        )
        tiles.append(tile)
        # Avoid OOM errors
        if (i + 1) % batch_size == 0:
            with transaction.atomic():
                Tile.objects.bulk_create(tiles, batch_size=batch_size // 8)
            logger.info(f"Got {len(tiles)} tiles")
            del tiles[:]
            gc.collect()
    if tiles:  # Save last batch
        Tile.objects.bulk_create(tiles, batch_size=batch_size // 8)


def clean_outside(selected_city, batch_size) -> None:
    """
    Remove all tiles outside of the selected cities.

    Args:
        selected_city (DataFrame): The DataFrame of the selected cities.
        batch_size (int): The size of the batch to delete.

    Returns:
        None
    """
    # Clean useless tiles
    city_union_geom = selected_city.geometry.union_all()
    print("Deleting tiles out of the cities")
    total_records = Tile.objects.all().count()
    total_deleted = 0
    for start in tqdm(range(0, total_records, batch_size * 10)):
        batch_ids = Tile.objects.all()[start : start + batch_size * 10].values_list(
            "id", flat=True
        )
        with transaction.atomic():
            deleted_count, _ = (
                Tile.objects.filter(id__in=batch_ids)
                .exclude(geometry__within=city_union_geom.wkt)
                .delete()
            )
            total_deleted += deleted_count
    print(f"Deleted {total_deleted} tiles")


class Command(BaseCommand):
    help = "Create grid and save it to DB"

    def add_arguments(self, parser):
        """Add arguments to the command."""
        parser.add_argument(
            "--insee_code_city",
            type=str,
            required=False,
            default=None,
            help="The INSEE code of the city or cities to process. If multiple cities, please separate with comma (e.g. --insee_code='69266,69382')",
        )
        parser.add_argument(
            "--grid-size", type=int, default=4, help="Grid size in meters"
        )
        parser.add_argument(
            "--grid-type", type=int, default=1, help="Hexagonal (1) or square (2) grid."
        )
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete already existing tiles.",
        )
        parser.add_argument(
            "--keep_outside",
            action="store_true",
            help="Keep tiles outside of the city selection (by default, they are deleted).",
        )

    @staticmethod
    def _remove_duplicates() -> None:
        """Deletes duplicates in the Tiles model based on geometry."""
        duplicates = (
            Tile.objects.values("geometry")
            .annotate(count=Count("id"))
            .filter(count__gt=1)
        )

        for duplicate in duplicates:
            geometry = duplicate["geometry"]
            duplicate_cities = Tile.objects.filter(geometry=geometry)
            # Keep the first and delete the rest
            ids_to_delete = duplicate_cities.values_list("id", flat=True)[1:]
            Tile.objects.filter(id__in=ids_to_delete).delete()
        print(f"Removed duplicates for {duplicates.count()} entries.")

    @staticmethod
    def _create_grid_city(
        city, batch_size, logger, grid_type, unit, a, grid_size, delete
    ):
        """
        Create grid for a specific city.

        Args:
            city (City): The city object with geometry, id and name.
            batch_size (int): The size of the batch to save to the DB.
            logger (Logger): The logger object.
            grid_type (int): The type of grid to create.
            unit (float): The size of the hexagon in meters (for hexagonal grid only).
            a (float): The ratio of the hexagon (for hexagonal grid only).
            grid_size (int): The size of the grid in meters (for square grid).

        Returns:
            None
        """
        print(f"Selected city: {city.name} with id {city.id}.")
        tiles_queryset = Tile.objects.filter(
            geometry__within=GEOSGeometry(city.geometry.wkt)
        )
        total_records = tiles_queryset.count()
        print(f"Number tiles already in the DB: {total_records}. \n")
        if delete or (city.tiles_generated is False):
            # Clean if asked or if not all Tiles have been generated
            print("These tiles will be deleted and new one recomputed.")
            City.objects.filter(id=city.id).update(tiles_generated=False)
            for start in tqdm(range(0, total_records, batch_size)):
                batch_ids = tiles_queryset[start : start + batch_size].values_list(
                    "id", flat=True
                )
                with transaction.atomic():
                    Tile.objects.filter(id__in=batch_ids).delete()
            print(f"Deleted {total_records} tiles.")
        elif city.tiles_generated:
            return
        print("Creating new tiles.")
        if grid_type == 1:  # Hexagonal grid
            create_hexs_for_city(city, unit, a, logger, int(1e4))
        elif grid_type == 2:  # square grid
            create_squares_for_city(city, grid_size, logger, int(1e4))
        City.objects.filter(id=city.id).update(tiles_generated=True)

    def handle(self, *args, **options):
        """Create grid and save it to DB."""
        batch_size = int(1e4)  # Depends on your RAM
        logger = logging.getLogger(__name__)
        insee_code_city = options["insee_code_city"]
        grid_size = options["grid_size"]
        grid_type = options["grid_type"]
        keep_outside = options["keep_outside"]
        delete = options["delete"]
        if grid_type not in [1, 2]:
            raise ValueError("Grid type should be either 1 (hexagonal) or 2 (square).")
        selected_city = select_city(insee_code_city)
        desired_area = grid_size * grid_size
        unit = np.sqrt((2 * desired_area) / (3 * np.sqrt(3)))
        a = np.sin(np.pi / 3)
        total_city = len(selected_city)
        processed_city = 0
        with ThreadPoolExecutor(max_workers=12) as executor:
            future_to_city = {
                executor.submit(
                    self._create_grid_city,
                    city,
                    batch_size,
                    logger,
                    grid_type,
                    unit,
                    a,
                    grid_size,
                    delete,
                ): city
                for city in selected_city.itertuples()
            }
            for future in as_completed(future_to_city):
                future.result()
                city = future_to_city.pop(future)
                processed_city += 1
                print(
                    f"Processed city: {processed_city} / {total_city} (city: {city.name})."
                )
                gc.collect()  # just to be sure gc is called...
        print("Removing duplicates...")
        self._remove_duplicates()
        if keep_outside is False:
            clean_outside(selected_city, batch_size)
