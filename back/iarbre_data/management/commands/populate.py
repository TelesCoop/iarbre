from django.core.management.base import BaseCommand
from shapely.geometry.polygon import Polygon
from iarbre_data.models import City, Tile, Lcz, Vulnerability, Data
from iarbre_data.utils.database import select_city
from api.utils.mvt_generator import MVTGenerator

from iarbre_data.utils.utils_populate import (
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
        mvt_generator.generate_tiles(ignore_existing=False)

    def _generate_lcz_zones(self):
        lczs = Lcz.objects.filter(
            geometry__intersects=GEOSGeometry(self.city.geometry.wkt)
        )
        if lczs.count() == 16:
            self.stdout.write("LCZ already computed")
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
        vulnerabilities = Vulnerability.objects.filter(
            geometry__intersects=GEOSGeometry(self.city.geometry.wkt)
        )
        if vulnerabilities.count() == 81:
            self.stdout.write("Vulnerability already computed")

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
            details = {
                "_expo_jour_note_dens_bati_vol": random.choice([0, 2, 4]),
                "_expo_jour_note_sky_view_factor": random.choice([-2, 0, 4]),
                "_expo_jour_note_canyon": random.choice([-2, 2, 4]),
                "_expo_jour_note_vegetation_haute": random.choice([-1, -2]),
                "_expo_jour_note_vegetation": random.choice([-2, -1, 0, 1]),
                "_expo_jour_note_eau": random.choice([-2, -1, 1]),
                "_expo_jour_note_permeabilite": random.choice([-1, 2, 3]),
                "_expo_jour_note_proxi_foret": random.choice([-1, 0]),
                "_expo_jour_note_proxi_eau": random.choice([-1, 0]),
                "_expo_jour_note_effusivite_thermique": random.choice([0, 2, 4]),
                "_expo_jour_note_albedo": random.choice([-2, 1, 2]),
                "_expo_nuit_note_dens_bati_vol": random.choice([0, 2, 4]),
                "_expo_nuit_note_sky_view_factor": random.choice([-2, 0, 4]),
                "_expo_nuit_note_canyon": random.choice([-2, 2, 4]),
                "_expo_nuit_note_vegetation": random.choice([-2, -1, 0, 1]),
                "_expo_nuit_note_eau": random.choice([-2, -1, 1]),
                "_expo_nuit_note_permeabilite": random.choice([-1, 2, 3]),
                "_expo_nuit_note_proxi_foret": random.choice([-1, 0]),
                "_expo_nuit_note_proxi_eau": random.choice([-1, 0]),
                "_sensi_jour_note_densité_hab": random.choice([0, 2, 4]),
                "_sensi_jour_note_population_sensible_âge": random.choice([0, 1, 4]),
                "_sensi_jour_note_densité_occupation_logement": random.choice(
                    [1, 3, 5]
                ),
                "_sensi_jour_note_incofort_habitat": random.choice([0, 2, 6]),
                "_sensi_jour_note_qualité_air": random.choice([1, 2, 4]),
                "_sensi_jour_note_part_menage_1ind": random.choice([0, 1, 6]),
                "_sensi_nuit_note_densité_hab": random.choice([0, 2, 4]),
                "_sensi_jour_note_densite_emploi": random.choice([0, 2, 3]),
                "_sensi_nuit_note_population_sensible_âge": random.choice([0, 1, 4]),
                "_sensi_nuit_note_densité_occupation_logement": random.choice(
                    [1, 3, 5]
                ),
                "_sensi_nuit_note_incofort_habitat": random.choice([0, 2, 6]),
                "_sensi_nuit_note_qualité_air": random.choice([1, 2, 4]),
                "_sensi_nuit_note_part_menage_1ind": random.choice([1, 2, 4]),
                "_capaf_jour_note_menpauv": random.choice([0, 3, 6]),
                "_capaf_jour_note_offremed": random.choice([0, 2]),
                "_capaf_jour_note_accesurgences": random.choice([0, 1, 2]),
                "_capaf_jour_note_proxiespacevert": random.choice([0, 1, 2]),
                "_capaf_jour_note_vegetation_haute": random.choice([0, 1, 2]),
                "_capaf_nuit_note_menpauv": random.choice([0, 3, 6]),
                "_capaf_nuit_note_accesurgences": random.choice([0, 1, 2]),
                "_capaf_nuit_note_proxiespacevert": random.choice([0, 1, 2]),
                "_capaf_nuit_note_vegetation_haute": random.choice([0, 1, 2]),
            }

            vul, created = Vulnerability.objects.update_or_create(
                geometry=geometry.wkt,
                defaults={
                    "vulnerability_index_day": i,
                    "vulnerability_index_night": j,
                    "expo_index_day": (i + j + 1) % 4,
                    "expo_index_night": (i + j + 2) % 4,
                    "capaf_index_day": (i + j + 3) % 4,
                    "capaf_index_night": (i + j + 4) % 4,
                    "sensibilty_index_day": (i + j + 5) % 4,
                    "sensibilty_index_night": (i + j + 6) % 4,
                    "details": details,
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"> Vulnerability created with ID {vul.id}")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"> Vulnerability with ID {vul.id} updated")
                )

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

    def _generate_qpv_data(self):
        qpv_data = Data.objects.filter(
            geometry__intersects=GEOSGeometry(self.city.geometry.wkt), factor="QPV"
        )
        if qpv_data.exists():
            self.stdout.write("QPV data already exists")
            return

        (x, y) = self.city_center
        qpv_size = 800
        x_offset = x - qpv_size / 2
        y_offset = y - qpv_size / 2

        qpv_geometry = Polygon(
            [
                (x_offset, y_offset),
                (x_offset + qpv_size, y_offset),
                (x_offset + qpv_size, y_offset + qpv_size),
                (x_offset, y_offset + qpv_size),
                (x_offset, y_offset),
            ]
        )

        qpv = Data(
            geometry=qpv_geometry.wkt,
            factor="QPV",
            metadata="Generated QPV zone for testing",
        )
        qpv.save()
        self.stdout.write(self.style.SUCCESS("> QPV data generated"))

    def handle(self, *args, **options):
        self._create_city_and_iris()
        self.city = City.objects.get(code=CITY_CODE)

        self._generate_plantability_tiles()
        self.generate_plantability_mvt_tiles()

        self._generate_lcz_zones()
        self.generate_lcz_mvt_tiles()

        self.generate_vulnerability_zones()
        self.generate_vulnerability_mvt_tiles()

        self._generate_qpv_data()
        self.stdout.write(self.style.SUCCESS("Successfully populated"))
