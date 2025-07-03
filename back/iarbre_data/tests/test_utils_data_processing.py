from django.test import TestCase
import geopandas as gpd
from django.contrib.gis.geos import Point as GEOSPoint
from iarbre_data.settings import TARGET_PROJ
from iarbre_data.utils.data_processing import apply_actions, make_valid, geocode_address
from shapely.geometry import Polygon, Point


class UtilsDataProcessingTestCase(TestCase):
    def setUp(self):
        self.df = gpd.GeoDataFrame(
            {
                "geometry": [
                    Point(1, 1),
                    Point(2, 2),
                    Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                    Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                ],
                "type": ["Point", "Point", "Polygon", "Polygon"],
                "value": [1, 2, 3, 4],
            },
            crs=TARGET_PROJ,
        )

    def test_apply_actions(self):
        actions = {"filter": {"name": "type", "value": "Point"}}
        result = apply_actions(self.df, actions)
        self.assertEqual(len(result), 0)  # should filter out points
        actions = {"filter": {"name": "type", "value": "Polygon"}}
        result = apply_actions(self.df, actions)
        self.assertEqual(len(result), 2)
        actions = {
            "filters": [{"name": "value", "value": 3}, {"name": "value", "value": 4}]
        }
        result = apply_actions(self.df, actions)
        self.assertEqual(len(result), 2)
        actions = {"union": True}
        result = apply_actions(self.df, actions)
        self.assertEqual(len(result), 1)
        self.assertTrue(result.iloc[0].geometry.geom_type == "Polygon")

    def test_make_valid(self):
        # Create a valid polygon
        valid_polygon = self.df.iloc[2].geometry
        self.assertTrue(valid_polygon.is_valid)
        result = make_valid(valid_polygon)
        self.assertTrue(result.is_valid)
        self.assertEqual(result, valid_polygon)

        # Create an invalid polygon (not closed)
        invalid_polygon = Polygon([(0, 0), (1, 1), (1, 0), (0, 1)])  # self intersecting
        self.assertFalse(invalid_polygon.is_valid)
        result = make_valid(invalid_polygon)
        self.assertTrue(result.is_valid)
        self.assertNotEqual(result, invalid_polygon)

    def test_geocode_address(self):
        address = "20 rue du lac, 69003 Lyon"
        result = geocode_address(address)

        self.assertIsInstance(result, GEOSPoint)
        self.assertEqual(result.srid, 2154)

        x, y = result.coords
        self.assertTrue(830000 < x < 860000)
        self.assertTrue(6510000 < y < 6530000)
