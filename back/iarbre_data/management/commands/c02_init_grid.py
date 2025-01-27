"""Create a grid over the metropole or a selection of city and save it to DB"""
import logging

from concurrent.futures import ThreadPoolExecutor, as_completed
from django.contrib.gis.geos import Polygon, GEOSGeometry
from django.core.management import BaseCommand


from iarbre_data.management.commands.utils import select_city
from iarbre_data.models import Iris, Tile, City
from iarbre_data.settings import TARGET_PROJ, TARGET_MAP_PROJ

from iarbre_data.management.commands.utils import (
    load_geodataframe_from_db,
    remove_duplicates,
)

import numpy as np
import gc
import itertools
from shapely.geometry import Point
from tqdm import tqdm
from django.db import transaction


def create_tiles_for_city(
    city, grid_size, tile_shape_cls, logger, batch_size=int(1e6), unit=None, a=None
) -> None:
    """
    Create tiles (square or hexagonal) for a specific city.

    Args:
        city (GeoPandas DataFrame): City GeoDataFrame.
        grid_size (float): The size of the grid in meters.
        tile_shape_cls (class): Class to generate individual tile shapes.
        logger (Logger): The logger object.
        batch_size (int): The size of the batch to save to DB.
        unit (float, optional): Parameter for hexagonal tiles.
        a (float, optional): Parameter for hexagonal tiles.

    Returns:
        None
    """
    city_geom = city.geometry
    city_id = city.id
    xmin, ymin, xmax, ymax = city_geom.bounds
    # Bounds for the generation
    xmin, ymin, xmax, ymax = tile_shape_cls.adjust_bounds(
        xmin, ymin, xmax, ymax, grid_size, a
    )

    tiles = []
    tile_count = 0

    for x, y in tqdm(
        tile_shape_cls.tile_positions(xmin, ymin, xmax, ymax, grid_size, unit, a)
    ):
        point = Point([x, y])
        if not city_geom.covers(point):
            continue

        tile_count += 1
        polygon = tile_shape_cls.create_tile_polygon(x, y, grid_size, unit, a)

        iris_id = tile_shape_cls.get_iris_id(polygon)

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
        if tile_count % batch_size == 0:
            with transaction.atomic():
                Tile.objects.bulk_create(tiles, batch_size=batch_size // 8)
            logger.info(f"Got {len(tiles)} tiles")
            tiles.clear()
            gc.collect()

    if tiles:  # Save last batch
        Tile.objects.bulk_create(tiles, batch_size=batch_size // 8)
    City.objects.filter(id=city.id).update(tiles_generated=True)


class TileShape:
    @staticmethod
    def get_iris_id(polygon):
        iris_id = Iris.objects.filter(geometry__intersects=polygon)
        if iris_id:
            return iris_id[0].id
        return None


class SquareTileShape(TileShape):
    """Generate square tile."""

    @staticmethod
    def adjust_bounds(xmin, ymin, xmax, ymax, grid_size, a=None):
        """Snap bounds to the nearest grid alignment."""
        xmin = np.floor(xmin / grid_size) * grid_size
        ymin = np.floor(ymin / grid_size) * grid_size
        xmax = np.ceil(xmax / grid_size) * grid_size
        ymax = np.ceil(ymax / grid_size) * grid_size
        return xmin, ymin, xmax, ymax

    @staticmethod
    def tile_positions(xmin, ymin, xmax, ymax, grid_size, unit=None, a=None):
        """Generate an iterator for all the position where to create a tile."""
        return itertools.product(
            np.arange(xmin, xmax + grid_size, grid_size),
            np.arange(ymin, ymax + grid_size, grid_size),
        )

    @staticmethod
    def create_tile_polygon(x, y, grid_size, unit=None, a=None):
        """Create a single square and round geometries to optimize storage."""
        x1 = x - grid_size
        y1 = y + grid_size
        return Polygon.from_bbox([round(x, 2) for x in [x, y, x1, y1]])


class HexTileShape(TileShape):
    """Generate hexagonal tile."""

    @staticmethod
    def adjust_bounds(xmin, ymin, xmax, ymax, grid_size, a):
        """Snap bounds to the nearest grid alignment."""
        hex_width = 3 * grid_size
        hex_height = 2 * grid_size * a
        xmin = hex_width * (np.floor(xmin / hex_width) - 1)
        ymin = hex_height * (np.floor(ymin / hex_height) - 1)
        xmax = hex_width * (np.ceil(xmax / hex_width) + 1)
        ymax = hex_height * (np.ceil(ymax / hex_height) + 1)
        return xmin, ymin, xmax, ymax

    @staticmethod
    def tile_positions(xmin, ymin, xmax, ymax, grid_size, unit, a):
        """Generate an iterator for all the position where to create a tile."""
        cols = np.arange(xmin, xmax, 3 * unit)
        rows = np.arange(ymin, ymax, unit * a)
        return itertools.product(cols, rows)

    @staticmethod
    def create_tile_polygon(x, y, grid_size, unit, a):
        """Create a single hexagon and round geometries to optimize storage."""
        offset = 1.5 * unit if y / a % 2 != 0 else 0
        x0 = x + offset
        dim = [
            (x0, y),
            (x0 + unit, y),
            (x0 + (1.5 * unit), y + unit * a),
            (x0 + unit, y + 2 * unit * a),
            (x0, y + 2 * unit * a),
            (x0 - (0.5 * unit), y + unit * a),
            (x0, y),
        ]
        return Polygon([(round(x, 2), round(y, 2)) for (x, y) in dim], srid=TARGET_PROJ)


def clean_outside(selected_city, batch_size) -> None:
    """
    Remove all tiles outside the selected cities.

    Args:
        selected_city (DataFrame): The DataFrame of the selected cities.
        batch_size (int): The size of the batch to delete.

    Returns:
        None
    """
    batch_size = int(batch_size)
    if len(selected_city) > 1:
        city_union_geom = selected_city.geometry.union_all()
    else:
        city_union_geom = selected_city.geometry.values[0]
    print("Deleting tiles out of the cities")
    total_records = Tile.objects.all().count()
    total_deleted = 0
    qs = Tile.objects.all().values_list("id", flat=True)
    for start in tqdm(range(0, total_records, batch_size * 10)):
        batch_ids = qs[start : start + batch_size * 10]
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
            grid_size (float): The size of the grid in meters (for square grid).

        Returns:
            None
        """
        print(f"Selected city: {city.name} with id {city.id}.")
        # Get already existing tiles
        tiles_queryset = Tile.objects.filter(
            geometry__intersects=GEOSGeometry(city.geometry.wkt)
        )
        if len(tiles_queryset) > 0:  # Not empty database
            all_ids = load_geodataframe_from_db(tiles_queryset, ["id"]).id
            total_records = tiles_queryset.count()
            print(f"Number tiles already in the DB: {total_records}. \n")
            if delete or (city.tiles_generated is False):
                # Clean if asked or if not all Tiles have been generated
                print("These tiles will be deleted and new one recomputed.")
                City.objects.filter(id=city.id).update(tiles_generated=False)
                for start in tqdm(range(0, total_records, batch_size)):
                    batch_ids = all_ids[start : start + batch_size]
                    with transaction.atomic():
                        Tile.objects.filter(id__in=batch_ids).delete()
                print(f"Deleted {total_records} tiles.")
            elif city.tiles_generated:
                return
        print("Creating new tiles.")
        if grid_type == 1:  # Hexagonal grid
            create_tiles_for_city(
                city, grid_size, HexTileShape, logger, batch_size, unit, a
            )
        elif grid_type == 2:  # square grid
            create_tiles_for_city(city, grid_size, SquareTileShape, logger, batch_size)

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
        remove_duplicates()
        if keep_outside is False:
            clean_outside(selected_city, batch_size)
