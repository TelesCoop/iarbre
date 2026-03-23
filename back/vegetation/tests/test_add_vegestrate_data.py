import geopandas as gpd
from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry
from shapely.geometry import Polygon

from vegetation.management.commands.add_vegestrate_data import (
    save_vegestrate,
    simplify_geom,
    compute_city_vegetation_surfaces,
    STRATE_MAPPING,
    STRATE_TREES,
    STRATE_BUSHES,
    STRATE_GRASS,
)
from iarbre_data.models import Vegestrate, City
from iarbre_data.settings import SRID_DB, SRID_MAPLIBRE, SRID_DOWNLOADED_DATA


class AddVegestrateDataTest(TestCase):
    def setUp(self):
        Vegestrate.objects.all().delete()
        City.objects.all().delete()

    def test_vegestrate_model_creation(self):
        vegestrate = Vegestrate.objects.create(
            geometry=GEOSGeometry("POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))", srid=SRID_DB),
            map_geometry=GEOSGeometry(
                "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))", srid=SRID_MAPLIBRE
            ),
            strate="arborescent",
            surface=100.0,
        )
        self.assertEqual(Vegestrate.objects.count(), 1)
        self.assertEqual(vegestrate.strate, "arborescent")
        self.assertEqual(vegestrate.surface, 100.0)

    def test_save_vegestrate(self):
        polygons = [
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]),
            Polygon([(2, 0), (3, 0), (3, 1), (2, 1), (2, 0)]),
            Polygon([(4, 0), (5, 0), (5, 1), (4, 1), (4, 0)]),
        ]
        gdf = gpd.GeoDataFrame(
            {
                "geometry": polygons,
                "map_geometry": polygons,
                "class": [STRATE_TREES, STRATE_BUSHES, STRATE_GRASS],
            },
            crs=f"EPSG:{SRID_DB}",
        )
        save_vegestrate(gdf)
        self.assertEqual(Vegestrate.objects.count(), 3)
        self.assertEqual(
            Vegestrate.objects.filter(strate=STRATE_MAPPING[STRATE_TREES]).count(), 1
        )
        self.assertEqual(
            Vegestrate.objects.filter(strate=STRATE_MAPPING[STRATE_BUSHES]).count(), 1
        )
        self.assertEqual(
            Vegestrate.objects.filter(strate=STRATE_MAPPING[STRATE_GRASS]).count(), 1
        )

    def test_save_vegestrate_skips_unknown_strate(self):
        polygons = [
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]),
            Polygon([(2, 0), (3, 0), (3, 1), (2, 1), (2, 0)]),
        ]
        gdf = gpd.GeoDataFrame(
            {
                "geometry": polygons,
                "map_geometry": polygons,
                "class": [STRATE_TREES, 99],
            },
            crs=f"EPSG:{SRID_DB}",
        )
        save_vegestrate(gdf)
        self.assertEqual(Vegestrate.objects.count(), 1)

    def test_simplify_geom(self):
        polygons = [
            Polygon(
                [(4.8, 45.7), (4.81, 45.7), (4.81, 45.71), (4.8, 45.71), (4.8, 45.7)]
            ),
            Polygon(
                [(4.82, 45.7), (4.83, 45.7), (4.83, 45.71), (4.82, 45.71), (4.82, 45.7)]
            ),
        ]
        gdf = gpd.GeoDataFrame(
            {"geometry": polygons, "class": [1, 2]}, crs=f"EPSG:{SRID_DOWNLOADED_DATA}"
        )
        result = simplify_geom(gdf)
        self.assertIn("map_geometry", result.columns)
        self.assertEqual(result.crs.to_epsg(), SRID_DB)
        self.assertEqual(result["map_geometry"].values.crs.to_epsg(), SRID_MAPLIBRE)
        self.assertTrue(result["geometry"].is_valid.all())
        self.assertTrue(result["map_geometry"].is_valid.all())

    def test_compute_city_vegetation_surfaces(self):
        city = City.objects.create(
            geometry=GEOSGeometry(
                "POLYGON((0 0, 100 0, 100 100, 0 100, 0 0))", srid=SRID_DB
            ),
            code="69001",
            name="Lyon 1er",
        )
        Vegestrate.objects.create(
            geometry=GEOSGeometry(
                "POLYGON((10 10, 50 10, 50 50, 10 50, 10 10))", srid=SRID_DB
            ),
            strate=STRATE_MAPPING[STRATE_TREES],
            surface=1600.0,
        )
        Vegestrate.objects.create(
            geometry=GEOSGeometry(
                "POLYGON((60 10, 90 10, 90 40, 60 40, 60 10))", srid=SRID_DB
            ),
            strate=STRATE_MAPPING[STRATE_GRASS],
            surface=900.0,
        )
        compute_city_vegetation_surfaces()
        city.refresh_from_db()
        self.assertIsNotNone(city.trees_surface)
        self.assertIsNotNone(city.grass_surface)
        self.assertIsNotNone(city.total_vegetation_surface)
        trees = city.trees_surface or 0.0
        grass = city.grass_surface or 0.0
        total = city.total_vegetation_surface or 0.0
        self.assertGreater(trees, 0)
        self.assertEqual(city.bushes_surface, 0.0)
        self.assertGreater(grass, 0)
        self.assertGreater(total, 0)
        self.assertAlmostEqual(total, trees + grass)
