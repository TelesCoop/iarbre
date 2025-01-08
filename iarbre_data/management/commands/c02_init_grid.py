import gc
import itertools
import logging
import random

import numpy as np
from django.contrib.gis.geos import Polygon, GEOSGeometry
from django.core.management import BaseCommand
from django.db import transaction, close_old_connections
from django.db.models import Count
from tqdm import tqdm

from iarbre_data.management.commands.utils import select_city
from iarbre_data.models import Iris, Tile
from iarbre_data.settings import TARGET_PROJ, TARGET_MAP_PROJ


def create_squares_for_city(city_geom, grid_size, logger, batch_size=int(1e6)):
    """Create square tiles in the DB for a specific city"""
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
        # Create tile with random indice from -5 to 5
        tile = Tile(
            geometry=polygon,
            map_geometry=polygon.transform(TARGET_MAP_PROJ, clone=True),
            indice=random.uniform(-5, 5),
        )
        tiles.append(tile)
        # Avoid OOM errors
        if (i + 1) % batch_size == 0:
            Tile.objects.bulk_create(tiles, batch_size=batch_size)
            logger.info(f"Got {len(tiles)} tiles")
            tiles.clear()
            gc.collect()
    if tiles:  # Save last batch
        Tile.objects.bulk_create(tiles, batch_size=batch_size)
        close_old_connections()


def create_hexs_for_city(
    city,
    unit,
    a,
    logger,
    batch_size=int(1e6),
):
    """Create hexagonal tiles in the DB for a specific city"""
    city_geom = city.geometry
    city_id = city.id
    xmin, ymin, xmax, ymax = city_geom.bounds
    hex_width = 3 * unit
    hex_height = 2 * unit * a
    xmin = np.floor(xmin / hex_width) * hex_width
    ymin = np.floor(ymin / hex_height) * hex_height
    xmax = np.ceil(xmax / hex_width) * hex_width
    ymax = np.ceil(ymax / hex_height) * hex_height

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
        iris_id = Iris.objects.filter(geometry__intersects=hexagon)[0].id
        tile = Tile(
            geometry=hexagon,
            map_geometry=hexagon.transform(TARGET_MAP_PROJ, clone=True),
            indice=random.uniform(-5, 5),
            # Create tile with random indice from -5 to 5
            city_id=city_id,
            iris_id=iris_id,
        )
        tiles.append(tile)
        # Avoid OOM errors
        if (i + 1) % batch_size == 0:
            with transaction.atomic():
                Tile.objects.bulk_create(tiles, batch_size=batch_size // 4)
            logger.info(f"Got {len(tiles)} tiles")
            del tiles[:]
            gc.collect()
    if tiles:  # Save last batch
        Tile.objects.bulk_create(tiles, batch_size=batch_size)
        close_old_connections()


class Command(BaseCommand):
    help = "Create grid and save it to DB"

    def add_arguments(self, parser):
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
            "--clean_outside",
            type=bool,
            default=True,
            help="Detele tiles outside of the city boundaries of the selection or not.",
        )

    @staticmethod
    def _remove_duplicates():
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
    def _clean_outside(selected_city, batch_size, logger):
        """Remove all tiles outside of the selected cities"""
        # Clean useless tiles
        city_union_geom = selected_city.geometry.unary_union
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
                    .exclude(geometry__intersects=city_union_geom.wkt)
                    .delete()
                )
                total_deleted += deleted_count
        logger.info(f"Deleted {total_deleted} tiles")

    @staticmethod
    def _create_grid_city(city, batch_size, logger, grid_type, unit, a, grid_size):
        print(f"Selected city: {city.name} with id {city.id}.")
        tiles_queryset = Tile.objects.filter(
            geometry__intersects=GEOSGeometry(city.geometry.wkt)
        )
        total_records = tiles_queryset.count()
        print(
            f"Number tiles already in the DB: {total_records}. \n"
            f"These tiles will be deleted."
        )
        for start in tqdm(range(0, total_records, batch_size)):
            batch_ids = tiles_queryset[start : start + batch_size].values_list(
                "id", flat=True
            )
            with transaction.atomic():
                Tile.objects.filter(id__in=batch_ids).delete()
        print(f"Deleted {total_records} tiles.")
        print("Creating new tiles.")
        if grid_type == 1:  # Hexagonal grid
            create_hexs_for_city(city, unit, a, logger, int(1e4))
        elif grid_type == 2:  # square grid
            create_squares_for_city(city, grid_size, logger, int(1e4))

    def handle(self, *args, **options):
        batch_size = int(1e4)  # Depends on your RAM
        logger = logging.getLogger(__name__)
        insee_code_city = options["insee_code_city"]
        grid_size = options["grid_size"]
        grid_type = options["grid_type"]
        clean_outside = options["clean_outside"]
        if grid_type not in [1, 2]:
            raise ValueError("Grid type should be either 1 (hexagonal) or 2 (square).")
        selected_city = select_city(insee_code_city)
        desired_area = grid_size * grid_size
        unit = np.sqrt((2 * desired_area) / (3 * np.sqrt(3)))
        a = np.sin(np.pi / 3)
        for city in selected_city.itertuples():
            self._create_grid_city(
                city,
                batch_size,
                logger,
                grid_type,
                unit,
                a,
                grid_size,
            )
        print("Removing duplicates...")
        self._remove_duplicates()
        if clean_outside:
            self._clean_outside(selected_city, batch_size, logger)
