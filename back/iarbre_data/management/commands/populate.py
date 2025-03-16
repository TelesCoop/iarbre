from django.core.management.base import BaseCommand
from shapely.geometry.polygon import Polygon
from iarbre_data.models import City, Tile
from iarbre_data.management.commands.utils import select_city, load_geodataframe_from_db
from api.utils.mvt_generator import MVTGenerator

from iarbre_data.management.commands.c02_init_grid import (
    create_tiles_for_city,
    HexTileShape,
)
from django.contrib.gis.geos import GEOSGeometry
import numpy as np
import logging
import random


class Command(BaseCommand):
    help = "Small command to randomly populate the database with testing data"

    def _create_city_or_ignore(self):
        if City.objects.filter(code="38250").exists():
            # self.stdout.write("City already exists")
            # return
            City.objects.get(code="38250").delete()

        self.stdout.write("Create Villard-de-Lans")
        # coords = { "lat": 45.06397, "lng": 5.55076}
        x = 617907.7767156712
        y = 5631597.881683022

        radius = 1000  # in m
        city_geometry = Polygon(
            [
                (x - radius, y - radius),
                (x + radius, y - radius),
                (x + radius, y + radius),
                (x - radius, y + radius),
                (x - radius, y - radius),
            ]
        )
        # Ce n’est pas au bon endroit ^^
        city = City(
            name="Villard-de-Lans",
            code="38250",
            tiles_generated=False,
            tiles_computed=False,
            geometry=city_geometry.wkt,
        )
        city.save()
        self.stdout.write(self.style.SUCCESS("> City 'Villard-de-Lans' created"))

        # I am sure we can improve the readability of select_city
        selected_city = select_city("38250")

        # Create Hex tiles
        create_tiles_for_city(
            city=selected_city.iloc[0],
            grid_size=50,
            tile_shape_cls=HexTileShape,
            logger=logging.getLogger(__name__),
            batch_size=int(1e6),
            side_length=50,
            height_ratio=np.sin(np.pi / 3),
        )

        self._generate_plantability_tiles()

    def _generate_plantability_tiles(self):
        random.seed(38250)
        city = City.objects.get(code="38250")
        tiles = Tile.objects.filter(
            geometry__intersects=GEOSGeometry(city.geometry.wkt)
        )
        Tile.objects.bulk_update(
            (
                Tile(id=tile.id, plantability_normalized_indice=random.random())
                for tile in tiles
            ),
            ["plantability_normalized_indice"],
        )
        tiles = Tile.objects.filter(
            geometry__intersects=GEOSGeometry(city.geometry.wkt)
        )
        print(list(t.plantability_normalized_indice for t in tiles))

    def _generate_mvt(self):
        city = City.objects.get(code="38250")
        tiles = Tile.objects.filter(
            geometry__intersects=GEOSGeometry(city.geometry.wkt)
        )

        mvt_generator = MVTGenerator(
            queryset=tiles,
            zoom_levels=(12, 16),
            datatype=Tile.datatype,
            geolevel=Tile.geolevel,
            number_of_thread=4,
        )
        mvt_generator.generate_tiles()

    def handle(self, *args, **options):
        self._create_city_or_ignore()
        self._generate_mvt()

        self.stdout.write("IP")

        self.stdout.write("IP")
        self.stdout.write(self.style.SUCCESS("Successfully populated"))
