from django.core.management.base import BaseCommand
from shapely.geometry.polygon import Polygon
from iarbre_data.models import City, Tile, Lcz, Vulnerability
from iarbre_data.utils.database import select_city
from api.utils.mvt_generator import MVTGenerator

from iarbre_data.management.commands.c02_init_grid import (
    create_tiles_for_city,
    HexTileShape,
)
from django.contrib.gis.geos import GEOSGeometry

import numpy as np
import logging
import random
import itertools
from iarbre_data.management.commands.c01_insert_cities_and_iris import (
    Command as InsertIrisCommand,
)

CITY_CODE = "38250"


class Command(BaseCommand):
    help = "Small command to randomly populate the database with testing data"

    # GPS coords  { "lat": 45.06397, "lng": 5.55076}
    # Below in Lambert-93
    city_center = (900733.8693696633, 6443766.2240856625)

    def _create_city_and_iris(self):
        if City.objects.filter(code=CITY_CODE).exists():
            self.stdout.write("City already exists")
            return

        self.stdout.write("Create Villard-de-Lans")

        (x, y) = self.city_center
        radius = 2500  # in m
        city_geometry = Polygon(
            [
                (x - radius, y - radius),
                (x + radius, y - radius),
                (x + radius, y + radius),
                (x - radius, y + radius),
                (x - radius, y - radius),
            ]
        )

        city = City(
            name="Villard-de-Lans",
            code=CITY_CODE,
            geometry=city_geometry.wkt,
        )
        city.save()

        city = City.objects.filter(code=CITY_CODE)
        InsertIrisCommand._insert_iris(city)

        self.stdout.write(self.style.SUCCESS("> City 'Villard-de-Lans' created"))

        selected_city = select_city(CITY_CODE)

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
        self.stdout.write(self.style.SUCCESS("> Tiles created"))

    def _generate_plantability_tiles(self):
        random.seed(0)

        tiles = Tile.objects.filter(
            geometry__intersects=GEOSGeometry(self.city.geometry.wkt)
        )
        # If all are generated, skip. Otherwise, regenerate all tiles
        # as we want a reproducible plantability score
        if tiles.filter(plantability_normalized_indice__isnull=True).count() == 0:
            self.stdout.write("Plantability indices already computed")
            return

        Tile.objects.bulk_update(
            (
                Tile(id=tile.id, plantability_normalized_indice=random.randint(0, 10))
                for tile in tiles
            ),
            ["plantability_normalized_indice"],
            batch_size=1000,
        )
        self.stdout.write(self.style.SUCCESS("> Plantability Score computed"))

    def _generate_mvt(self, queryset, datatype, geolevel):
        mvt_generator = MVTGenerator(
            queryset=queryset,
            zoom_levels=(13, 13),
            datatype=datatype,
            geolevel=geolevel,
            number_of_thread=4,
        )
        mvt_generator.generate_tiles(ignore_existing=True)

    def _generate_lcz_zones(self):
        lczs = Lcz.objects.filter(
            geometry__intersects=GEOSGeometry(self.city.geometry.wkt)
        )
        if lczs.count() == 16:
            return
        lczs.delete()

        (x0, y0) = self.city_center
        city_length = 2500
        x0 -= city_length / 2
        y0 -= city_length / 2

        indices = [
            None,
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
        ]

        lcz_length = city_length / 4
        for i, j in itertools.product(range(4), repeat=2):
            x = x0 + i * lcz_length
            y = y0 + j * lcz_length
            geometry = Polygon(
                (
                    (x, y),
                    (x + lcz_length, y),
                    (x + lcz_length, y + lcz_length),
                    (x, y + lcz_length),
                    (x, y),
                )
            )
            lcz = Lcz(
                geometry=geometry.wkt,
                lcz_index=indices[i + j * 4],
            )
            lcz.save()
        self.stdout.write(self.style.SUCCESS("> Lcz zones computed"))

    def generate_vulnerability_zones(self):
        vulnerabilities = Tile.objects.filter(
            geometry__intersects=GEOSGeometry(self.city.geometry.wkt)
        )
        if vulnerabilities.count() == 81:
            return
        vulnerabilities.delete()

        (x0, y0) = self.city_center
        city_length = 2500
        x0 -= city_length / 2
        y0 -= city_length / 2

        lcz_length = city_length / 9
        for i, j in itertools.product(range(9), repeat=2):
            x = x0 + i * lcz_length
            y = y0 + j * lcz_length
            geometry = Polygon(
                (
                    (x, y),
                    (x + lcz_length, y),
                    (x + lcz_length, y + lcz_length),
                    (x, y + lcz_length),
                    (x, y),
                )
            )
            vul = Vulnerability(
                geometry=geometry.wkt,
                vulnerability_index_day=i,
                vulnerability_index_night=j,
                expo_index_day=(i + j + 1) % 4,
                expo_index_night=(i + j + 2) % 4,
                capaf_index_day=(i + j + 3) % 4,
                capaf_index_night=(i + j + 4) % 4,
                sensibilty_index_day=(i + j + 5) % 4,
                sensibilty_index_night=(i + j + 6) % 4,
            )
            vul.save()

    def generate_lcz_mvt_tiles(self):
        lczs = Lcz.objects.filter(
            geometry__intersects=GEOSGeometry(self.city.geometry.wkt)
        )

        self._generate_mvt(lczs, Lcz.datatype, Lcz.geolevel)
        self.stdout.write(self.style.SUCCESS("> MVT Tiles for LCZ computed"))

    def generate_plantability_mvt_tiles(self):
        tiles = Tile.objects.filter(
            geometry__intersects=GEOSGeometry(self.city.geometry.wkt)
        )
        self._generate_mvt(tiles, Tile.datatype, Tile.geolevel)
        self.stdout.write(self.style.SUCCESS("> MVT Tiles for plantability computed"))

    def generate_vulnerability_mvt_tiles(self):
        vulnerabilities = Vulnerability.objects.filter(
            geometry__intersects=GEOSGeometry(self.city.geometry.wkt)
        )
        self._generate_mvt(
            vulnerabilities, Vulnerability.datatype, Vulnerability.geolevel
        )
        self.stdout.write(self.style.SUCCESS("> MVT Tiles for vulnerability computed"))

    def handle(self, *args, **options):
        self._create_city_and_iris()
        self.city = City.objects.get(code=CITY_CODE)

        self._generate_plantability_tiles()
        self.generate_plantability_mvt_tiles()

        self._generate_lcz_zones()
        self.generate_lcz_mvt_tiles()

        self.generate_vulnerability_zones()
        self.generate_vulnerability_mvt_tiles()
        self.stdout.write(self.style.SUCCESS("Successfully populated"))
