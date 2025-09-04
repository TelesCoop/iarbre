import geopandas as gpd
from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry
from shapely.geometry import Polygon
from iarbre_data.management.commands.import_lcz import (
    Command,
    save_geometries,
)
from iarbre_data.models import Lcz
from iarbre_data.factories import CityFactory
from iarbre_data.utils.data_processing import make_valid
from iarbre_data.data_config import LCZ
import random


class ImportLczCommandTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_city = CityFactory(code="69001", name="Lyon 1er")

    def setUp(self):
        self.command = Command()
        Lcz.objects.all().delete()

    def test_lcz_model_creation(self):
        initial_count = Lcz.objects.count()

        lcz = Lcz.objects.create(
            geometry=GEOSGeometry(
                "POLYGON((4.8 45.7, 4.81 45.7, 4.81 45.71, 4.8 45.71, 4.8 45.7))",
                srid=2154,
            ),
            map_geometry=GEOSGeometry(
                "POLYGON((4.8 45.7, 4.81 45.7, 4.81 45.71, 4.8 45.71, 4.8 45.7))",
                srid=3857,
            ),
            lcz_index="1",
            lcz_description="Compact high-rise",
            details={"hre": 0.5, "are": 0.3},
        )

        self.assertEqual(Lcz.objects.count(), initial_count + 1)
        self.assertEqual(lcz.lcz_index, "1")
        self.assertEqual(lcz.lcz_description, "Compact high-rise")

    def test_lcz_model_with_all_details(self):
        lcz = Lcz.objects.create(
            geometry=GEOSGeometry(
                "POLYGON((4.8 45.7, 4.81 45.7, 4.81 45.71, 4.8 45.71, 4.8 45.7))",
                srid=2154,
            ),
            map_geometry=GEOSGeometry(
                "POLYGON((4.8 45.7, 4.81 45.7, 4.81 45.71, 4.8 45.71, 4.8 45.7))",
                srid=3857,
            ),
            lcz_index="2",
            lcz_description="Compact midrise",
            details={
                "hre": 0.5,
                "are": 0.3,
                "bur": 0.2,
                "ror": 0.1,
                "bsr": 0.4,
                "war": 0.6,
                "ver": 0.7,
                "vhr": 0.8,
            },
        )

        self.assertEqual(lcz.lcz_index, "2")
        self.assertEqual(lcz.lcz_description, "Compact midrise")
        self.assertEqual(lcz.details["hre"], 0.5)
        self.assertEqual(lcz.details["vhr"], 0.8)
        self.assertEqual(len(lcz.details), 8)

    def test_save_geometries_with_real_geodataframe(self):
        # Create a real GeoDataFrame with test data
        polygons = [
            Polygon(
                [(4.8, 45.7), (4.81, 45.7), (4.81, 45.71), (4.8, 45.71), (4.8, 45.7)]
            ),
            Polygon(
                [(4.82, 45.7), (4.83, 45.7), (4.83, 45.71), (4.82, 45.71), (4.82, 45.7)]
            ),
        ]

        data = {
            "geometry": polygons,
            "map_geometry": polygons,
            "lcz": ["1", "2"],
            "hre": [0.5, 0.6],
            "are": [0.3, 0.4],
            "bur": [0.2, 0.3],
            "ror": [0.1, 0.2],
            "bsr": [0.4, 0.5],
            "war": [0.6, 0.7],
            "ver": [0.7, 0.8],
            "vhr": [0.8, 0.9],
        }

        gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")

        initial_count = Lcz.objects.count()
        save_geometries(gdf)

        self.assertEqual(Lcz.objects.count(), initial_count + 2)

        # Check first LCZ
        lcz1 = Lcz.objects.filter(lcz_index="1").first()
        self.assertIsNotNone(lcz1)
        self.assertEqual(lcz1.details["hre"], 0.5)
        self.assertEqual(lcz1.details["vhr"], 0.8)

        # Check second LCZ
        lcz2 = Lcz.objects.filter(lcz_index="2").first()
        self.assertIsNotNone(lcz2)
        self.assertEqual(lcz2.details["hre"], 0.6)
        self.assertEqual(lcz2.details["vhr"], 0.9)

    def test_save_geometries_large_batch(self):
        # Create a dataset larger than batch_size (10000)
        num_records = 15000
        polygons = [
            Polygon(
                [
                    (4.8 + i * 0.001, 45.7),
                    (4.81 + i * 0.001, 45.7),
                    (4.81 + i * 0.001, 45.71),
                    (4.8 + i * 0.001, 45.71),
                    (4.8 + i * 0.001, 45.7),
                ]
            )
            for i in range(num_records)
        ]
        lcz_name = list(LCZ.keys())
        data = {
            "geometry": polygons,
            "map_geometry": polygons,
            "lcz": [random.choice(lcz_name) for _ in range(num_records)],
            "hre": [0.5 + (i % 10) * 0.01 for i in range(num_records)],
            "are": [0.3 + (i % 10) * 0.01 for i in range(num_records)],
            "bur": [0.2 + (i % 10) * 0.01 for i in range(num_records)],
            "ror": [0.1 + (i % 10) * 0.01 for i in range(num_records)],
            "bsr": [0.4 + (i % 10) * 0.01 for i in range(num_records)],
            "war": [0.6 + (i % 10) * 0.01 for i in range(num_records)],
            "ver": [0.7 + (i % 10) * 0.01 for i in range(num_records)],
            "vhr": [0.8 + (i % 10) * 0.01 for i in range(num_records)],
        }

        gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")
        initial_count = Lcz.objects.count()
        save_geometries(gdf)

        self.assertEqual(Lcz.objects.count(), initial_count + num_records + 1)

    def test_make_valid_function(self):
        # Test with valid geometry
        valid_geom = Polygon(
            [(4.8, 45.7), (4.81, 45.7), (4.81, 45.71), (4.8, 45.71), (4.8, 45.7)]
        )
        result = make_valid(valid_geom)
        self.assertTrue(result.is_valid)

        # Test with None geometry
        result = make_valid(None)
        self.assertIsNone(result)

    def test_lcz_string_conversion(self):
        # Test with numeric string
        gdf_data = {
            "geometry": [
                Polygon(
                    [
                        (4.8, 45.7),
                        (4.81, 45.7),
                        (4.81, 45.71),
                        (4.8, 45.71),
                        (4.8, 45.7),
                    ]
                )
            ],
            "map_geometry": [
                Polygon(
                    [
                        (4.8, 45.7),
                        (4.81, 45.7),
                        (4.81, 45.71),
                        (4.8, 45.71),
                        (4.8, 45.7),
                    ]
                )
            ],
            "lcz": [1],  # Integer
            "hre": [0.5],
            "are": [0.3],
            "bur": [0.2],
            "ror": [0.1],
            "bsr": [0.4],
            "war": [0.6],
            "ver": [0.7],
            "vhr": [0.8],
        }

        gdf = gpd.GeoDataFrame(gdf_data, crs="EPSG:4326")
        gdf["lcz"] = gdf["lcz"].astype(str)  # This is what the command does

        save_geometries(gdf)

        lcz = Lcz.objects.first()
        self.assertEqual(lcz.lcz_index, "1")
        self.assertIsInstance(lcz.lcz_index, str)
