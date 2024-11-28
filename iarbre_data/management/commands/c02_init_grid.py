import itertools
import logging
import random
import geopandas as gpd

import numpy as np
from django.contrib.gis.geos import Polygon
from django.core.management import BaseCommand
from django.db import transaction
from tqdm import tqdm

from iarbre_data.management.commands.utils import load_geodataframe_from_db
from iarbre_data.models import City, Tile


class Command(BaseCommand):
    help = "Create grid and save it to DB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--grid-size", type=int, default=5, help="Grid size in meters"
        )
        parser.add_argument(
            "--insee_code_city",
            type=str,
            required=False,
            default=None,
            help="The INSEE code of the city or cities to process. If multiple cities, please separate with comma (e.g. --insee_code='69266,69382')",
        )

    def create_tiles_for_city(self, city, grid_size, logger, batch_size=int(1e6)):
        """Create the tiles in the DB for a specific city"""
        xmin, ymin, xmax, ymax = city.total_bounds

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
            x0, y0, x1, y1 = map(
                lambda v: round(v, number_of_decimals), (x0, y0, x1, y1)
            )

            # Create tile with random indice from -5 to 5
            tile = Tile(
                geometry=Polygon.from_bbox([x0, y0, x1, y1]),
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

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        insee_code_city = options["insee_code_city"]
        grid_size = options["grid_size"]
        # Delete records if already exist
        total_records = Tile.objects.count()
        batch_size = int(1e6)  # Depends on your RAM
        print("Deleting old tiles")
        for start in tqdm(range(0, total_records, batch_size)):
            batch_ids = Tile.objects.all()[start : start + batch_size].values_list(
                "id", flat=True
            )
            with transaction.atomic():
                Tile.objects.filter(id__in=batch_ids).delete()
        logger.info(f"Deleted {total_records} tiles")

        # get bounding box of all or a selected city
        if insee_code_city is not None:
            insee_code_city = insee_code_city.split(",")
            selected_city_qs = City.objects.filter(insee_code__in=insee_code_city)
            if not selected_city_qs.exists():
                raise ValueError(f"No city found with INSEE code {insee_code_city}")
            selected_city = load_geodataframe_from_db(
                selected_city_qs, ["name", "insee_code"]
            )
        else:
            selected_city = load_geodataframe_from_db(
                City.objects.all(), ["name", "insee_code"]
            )
        nb_city = len(selected_city)

        for index, row in selected_city.iterrows():
            city = gpd.GeoDataFrame(
                [row], columns=selected_city.columns, crs=selected_city.crs
            )
            print(f"Selected city: {city.name.iloc[0]} (on {nb_city} city).")
            self.create_tiles_for_city(city, grid_size, logger, int(1e4))
