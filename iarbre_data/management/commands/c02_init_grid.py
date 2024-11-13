import itertools
import logging
from functools import reduce

import geopandas as gpd
from django.contrib.gis.geos import Polygon
from django.core.management import BaseCommand
import shapely
import shapely.wkt
import numpy as np
from tqdm import tqdm

from iarbre_data.models import City, Tile
import random

class Command(BaseCommand):
    help = "Create grid and save it to DB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--grid-size", type=int, default=5, help="Grid size in meters"
        )

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        grid_size = options["grid_size"]

        n_deleted, _ = Tile.objects.all().delete()
        logger.info(f"Deleted {n_deleted} tiles")

        # get bounding box of all cities
        cities = City.objects.all()

        df = gpd.GeoDataFrame(
            [{"name": city.name, "geometry": city.geometry.transform(3857, clone=True)} for city in cities]
        )
        df.geometry = df["geometry"].apply(lambda el: shapely.wkt.loads(el.wkt))
        df = df.set_geometry("geometry")
        xmin, ymin, xmax, ymax = df.total_bounds

        tiles = []
        batch_size = int(1e5)  # Depends on your RAM
        for i, (x0, y0) in enumerate(tqdm(
            itertools.product(
                np.arange(xmin, xmax + grid_size, grid_size),
                np.arange(ymin, ymax + grid_size, grid_size),
            ))
        ):
            # Bounds
            x1 = x0 - grid_size
            y1 = y0 + grid_size

            # reduce precision of coordinates to optimize storage
            number_of_decimals = 2
            x0, y0, x1, y1 = map(lambda v: round(v, number_of_decimals), (x0, y0, x1, y1))

            # Create tile with random indice from -5 to 5
            tiles.append(Tile(geometry=Polygon.from_bbox([x0, y0, x1, y1]), indice=random.uniform(-5, 5)))

            # Avoid OOM errors
            if (i + 1) % batch_size == 0:
                Tile.objects.bulk_create(tiles, batch_size=batch_size)
                logger.info(f"got {len(tiles)} tiles")
                tiles.clear()  # Free memory by clearing the list

        if tiles: # Save last batch
            Tile.objects.bulk_create(tiles, batch_size=batch_size)
