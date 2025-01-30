from django.test import TestCase
from iarbre_data.management.commands.utils import (
    load_geodataframe_from_db,
    remove_duplicates,
    select_city,
)
from iarbre_data.factories import CityFactory
from iarbre_data.models import City
from django.contrib.gis.geos import Polygon
import geopandas as gpd


class UtilsTestCase(TestCase):
    def setUp(self):
        CityFactory.create_batch(10)

    def test_load_geodataframe_from_db(self):
        city_qs = City.objects.all()
        result_df = load_geodataframe_from_db(city_qs, [])
        self.assertIsInstance(result_df, gpd.GeoDataFrame)
        self.assertIn("geometry", result_df.columns)

        empty_queryset = City.objects.none()
        result_df = load_geodataframe_from_db(empty_queryset, [])
        self.assertIsInstance(result_df, gpd.GeoDataFrame)
        self.assertEqual(len(result_df), 0)

    def test_remove_duplicates(self):
        poly1 = Polygon.from_bbox(
            [844737.86651438, 6525626.23803353, 846991.45060761, 6528047.95246801]
        )
        poly1.srid = 2154
        CityFactory.create(geometry=poly1)
        CityFactory.create(geometry=poly1)
        remove_duplicates(City)
        qs = City.objects.all()
        self.assertEqual(len(qs), 11)

    def test_select_city(self):
        insee_code_city = None
        cities = select_city(insee_code_city=insee_code_city)
        self.assertEqual(len(cities), 10)
        CityFactory.create(code=69381)
        CityFactory.create(code=69382)
        insee_code_city = "69381,69382"
        cities = select_city(insee_code_city=insee_code_city)
        self.assertEqual(len(cities), 2)
