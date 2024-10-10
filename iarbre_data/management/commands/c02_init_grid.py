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
            "--grid-size", type=int, default=30, help="Grid size in meters"
        )

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        grid_size = options["grid_size"]

        n_deleted, _ = Tile.objects.all().delete()
        logger.info(f"Deleted {n_deleted} tiles")

        # get bounding box of all cities
        cities = City.objects.all()

        print(cities[0].geometry.srid)

        df = gpd.GeoDataFrame(
            [{"name": city.name, "geometry": city.geometry.transform(3857, clone=True)} for city in cities]
        )
        df.geometry = df["geometry"].apply(lambda el: shapely.wkt.loads(el.wkt))
        df = df.set_geometry("geometry")
        xmin, ymin, xmax, ymax = df.total_bounds

        tiles = []
        for x0, y0 in tqdm(
            itertools.product(
                np.arange(xmin, xmax + grid_size, grid_size),
                np.arange(ymin, ymax + grid_size, grid_size),
            )
        ):
            # Bounds
            x1 = x0 - grid_size
            y1 = y0 + grid_size

            # reduce precision of coordinates to optimize storage
            number_of_decimals = 6
            x0 = round(x0, number_of_decimals)
            y0 = round(y0, number_of_decimals)
            x1 = round(x1, number_of_decimals)
            y1 = round(y1, number_of_decimals)



            # Create tile with random indice from 0 to 1
            tiles.append(Tile(geometry=Polygon.from_bbox([x0, y0, x1, y1]), indice=random.uniform(0, 1)))

        logger.info(f"got {len(tiles)} tiles")
        Tile.objects.bulk_create(tiles, batch_size=1000)
