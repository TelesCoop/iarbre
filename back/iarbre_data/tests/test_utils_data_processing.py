from django.test import TestCase
import geopandas as gpd
from django.contrib.gis.geos import Point as GEOSPoint
from iarbre_data.settings import SRID_DB
from iarbre_data.utils.data_processing import (
    apply_actions,
    make_valid,
    geocode_address,
    subdivide,
)
import shapely
from shapely.geometry import LineString, MultiPolygon, Polygon, Point, box


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
            crs=SRID_DB,
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

    def test_apply_actions_subdivide_after_union(self):
        df = gpd.GeoDataFrame(
            geometry=[Point(0, 0).buffer(100, quad_segs=256)], crs=SRID_DB
        )
        result = apply_actions(df, {"union": True, "subdivide": 32})
        self.assertGreater(len(result), 1)
        self.assertEqual(set(result.geom_type), {"Polygon"})

    def test_apply_actions_subdivide_after_buffer_only(self):
        df = gpd.GeoDataFrame(geometry=[LineString([(0, 0), (1000, 0)])], crs=SRID_DB)
        result = apply_actions(df, {"buffer_size": 2, "subdivide": 8})
        self.assertGreater(len(result), 1)
        self.assertAlmostEqual(result.area.sum(), df.buffer(2).area.sum(), places=3)

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
        self.assertEqual(result.srid, SRID_DB)

        x, y = result.coords
        self.assertTrue(830000 < x < 860000)
        self.assertTrue(6510000 < y < 6530000)


class SubdivideTestCase(TestCase):
    def test_subdivide_bounds_vertices_and_keeps_area(self):
        circle = Point(0, 0).buffer(100, quad_segs=256)
        result = subdivide(gpd.GeoSeries([circle], crs=SRID_DB), max_vertices=32)
        self.assertGreater(len(result), 1)
        self.assertTrue(all(shapely.get_num_coordinates(g) <= 32 for g in result))
        self.assertAlmostEqual(result.union_all().area, circle.area, places=3)

    def test_subdivide_multipolygon_gives_polygons(self):
        multi = MultiPolygon([Point(0, 0).buffer(10), Point(100, 0).buffer(10)])
        result = subdivide(gpd.GeoSeries([multi], crs=SRID_DB))
        self.assertEqual(set(result.geom_type), {"Polygon"})
        self.assertAlmostEqual(result.area.sum(), multi.area, places=3)

    def test_subdivide_repairs_invalid_geometry(self):
        bowtie = Polygon([(0, 0), (10, 10), (10, 0), (0, 10)])
        result = subdivide(gpd.GeoSeries([bowtie], crs=SRID_DB))
        self.assertTrue(result.is_valid.all())
        self.assertAlmostEqual(result.area.sum(), 50, places=3)

    def test_subdivide_keeps_row_attributes(self):
        gdf = gpd.GeoDataFrame(
            {
                "lcz": ["2", "6"],
                "geometry": [
                    Point(0, 0).buffer(100, quad_segs=256),
                    Point(500, 0).buffer(1),
                ],
            },
            crs=SRID_DB,
        )
        result = subdivide(gdf, max_vertices=32)
        self.assertIsInstance(result, gpd.GeoDataFrame)
        self.assertEqual(result.crs, gdf.crs)
        self.assertGreater((result["lcz"] == "2").sum(), 1)
        self.assertEqual(list(result["lcz"].unique()), ["2", "6"])

    def test_subdivide_empty_input(self):
        result = subdivide(gpd.GeoSeries([], crs=SRID_DB))
        self.assertEqual(len(result), 0)

    def test_subdivide_maps_pieces_to_rows_across_batches(self):
        n = 1500
        gdf = gpd.GeoDataFrame(
            {
                "row_id": range(n),
                "geometry": [box(i * 10, 0, i * 10 + 5, 5) for i in range(n)],
            },
            crs=SRID_DB,
        )
        result = subdivide(gdf)
        self.assertEqual(len(result), n)
        for label, row_id, geom in zip(result.index, result["row_id"], result.geometry):
            self.assertEqual(int(geom.centroid.x // 10), row_id)
            self.assertEqual(label, row_id)
