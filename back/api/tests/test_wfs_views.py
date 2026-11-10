import json
import re

from django.test import TestCase, Client
from django.contrib.gis.geos import Polygon
from iarbre_data.settings import SRID_DB
from iarbre_data.models import City, Tile, Vegestrate

WFS_URL = "/api/wfs/"
CRS84 = "urn:ogc:def:crs:OGC::CRS84"
GML_POS_LIST = re.compile(r"<gml:posList[^>]*>([^<]+)<")
GML_ENVELOPE = re.compile(r"<gml:(?:lowerCorner|upperCorner)>([^<]+)<")
FLOAT4_BBOX_TOLERANCE = 1e-5

VILLARD_SQUARE = Polygon(
    (
        (898233, 6441266),
        (903233, 6441266),
        (903233, 6446266),
        (898233, 6446266),
        (898233, 6441266),
    ),
    srid=SRID_DB,
)
VILLARD_SQUARE_LON_LAT = VILLARD_SQUARE.transform(4326, clone=True)


def gml_values(pattern, body):
    return [float(v) for text in pattern.findall(body) for v in text.split()]


class WFSViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.city = City.objects.create(
            name="Villard-de-Lans", code="38250", geometry=VILLARD_SQUARE
        )
        self.tile = Tile.objects.create(
            geometry=VILLARD_SQUARE,
            plantability_indice=3.5,
            plantability_normalized_indice=7,
            city=self.city,
        )

    def test_get_capabilities_status(self):
        response = self.client.get(
            WFS_URL,
            {"SERVICE": "WFS", "REQUEST": "GetCapabilities"},
        )
        self.assertEqual(response.status_code, 200)

    def test_get_capabilities_content_type(self):
        response = self.client.get(
            WFS_URL,
            {"SERVICE": "WFS", "REQUEST": "GetCapabilities"},
        )
        self.assertIn("xml", response["content-type"])

    def test_get_capabilities_contains_service_title(self):
        response = self.client.get(
            WFS_URL,
            {"SERVICE": "WFS", "REQUEST": "GetCapabilities"},
        )
        self.assertIn(b"IArbre WFS", response.content)

    def test_get_capabilities_contains_feature_type(self):
        response = self.client.get(
            WFS_URL,
            {"SERVICE": "WFS", "REQUEST": "GetCapabilities"},
        )
        self.assertIn(b"plantability", response.content)

    def test_describe_feature_type_status(self):
        response = self.client.get(
            WFS_URL,
            {
                "SERVICE": "WFS",
                "VERSION": "2.0.0",
                "REQUEST": "DescribeFeatureType",
                "TYPENAMES": "plantability",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_describe_feature_type_exposes_fields(self):
        response = self.client.get(
            WFS_URL,
            {
                "SERVICE": "WFS",
                "VERSION": "2.0.0",
                "REQUEST": "DescribeFeatureType",
                "TYPENAMES": "plantability",
            },
        )
        self.assertIn(b"plantability_indice", response.content)
        self.assertIn(b"plantability_normalized_indice", response.content)

    def test_get_feature_status(self):
        response = self.client.get(
            WFS_URL,
            {
                "SERVICE": "WFS",
                "VERSION": "2.0.0",
                "REQUEST": "GetFeature",
                "TYPENAMES": "plantability",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_get_feature_returns_tile(self):
        response = self.client.get(
            WFS_URL,
            {
                "SERVICE": "WFS",
                "VERSION": "2.0.0",
                "REQUEST": "GetFeature",
                "TYPENAMES": "plantability",
            },
        )
        body = b"".join(response.streaming_content)
        self.assertIn(b"plantability_indice", body)

    def test_get_feature_without_data(self):
        Tile.objects.all().delete()
        response = self.client.get(
            WFS_URL,
            {
                "SERVICE": "WFS",
                "VERSION": "2.0.0",
                "REQUEST": "GetFeature",
                "TYPENAMES": "plantability",
            },
        )
        self.assertEqual(response.status_code, 200)
        body = b"".join(response.streaming_content)
        self.assertIn(b'numberReturned="0"', body)

    def test_get_feature_geojson_has_no_geometry_name(self):
        response = self.client.get(
            WFS_URL,
            {
                "SERVICE": "WFS",
                "VERSION": "2.0.0",
                "REQUEST": "GetFeature",
                "TYPENAMES": "plantability",
                "OUTPUTFORMAT": "geojson",
            },
        )
        feature = json.loads(b"".join(response.streaming_content))["features"][0]
        self.assertNotIn("geometry_name", feature)
        self.assertNotIn("name", feature["properties"])
        self.assertEqual(feature["properties"]["city_code"], "38250")

    def _get_in_degrees(self, srs_name=CRS84, **params):
        response = self.client.get(
            WFS_URL,
            {
                "SERVICE": "WFS",
                "VERSION": "2.0.0",
                "TYPENAMES": "plantability",
                "SRSNAME": srs_name,
                **params,
            },
        )
        self.assertEqual(response.status_code, 200)
        return b"".join(response.streaming_content).decode()

    def _assert_coordinates(self, coordinates, expected, tolerance=1e-6):
        self.assertEqual(len(coordinates), len(expected))
        for value, reference in zip(coordinates, expected):
            self.assertAlmostEqual(value, reference, delta=tolerance)

    def _assert_lon_lat_ring(self, coordinates):
        self._assert_coordinates(
            coordinates,
            [v for point in VILLARD_SQUARE_LON_LAT.coords[0] for v in point],
        )

    def _assert_gml_lon_lat_ring(self, body):
        self._assert_lon_lat_ring(gml_values(GML_POS_LIST, body))

    def _assert_geojson_lon_lat_ring(self, body):
        ring = json.loads(body)["features"][0]["geometry"]["coordinates"][0]
        self._assert_lon_lat_ring([value for point in ring for value in point])

    def test_get_feature_geojson_in_crs84(self):
        self._assert_geojson_lon_lat_ring(
            self._get_in_degrees(REQUEST="GetFeature", OUTPUTFORMAT="geojson")
        )

    def test_get_feature_gml_in_crs84(self):
        body = self._get_in_degrees(REQUEST="GetFeature")
        self._assert_gml_lon_lat_ring(body)
        self._assert_coordinates(
            gml_values(GML_ENVELOPE, body),
            VILLARD_SQUARE_LON_LAT.extent,
            FLOAT4_BBOX_TOLERANCE,
        )

    def test_get_property_value_in_crs84(self):
        self._assert_gml_lon_lat_ring(
            self._get_in_degrees(REQUEST="GetPropertyValue", VALUEREFERENCE="geometry")
        )

    def test_get_feature_csv_in_crs84(self):
        body = self._get_in_degrees(REQUEST="GetFeature", OUTPUTFORMAT="csv")
        ring = re.search(r"POLYGON\(\(([^)]+)\)\)", body).group(1)
        self._assert_lon_lat_ring([float(v) for v in re.split(r"[ ,]", ring)])

    def test_get_feature_geojson_in_epsg_4326(self):
        self._assert_geojson_lon_lat_ring(
            self._get_in_degrees(
                "EPSG:4326", REQUEST="GetFeature", OUTPUTFORMAT="geojson"
            )
        )

    def test_get_feature_gml_in_epsg_4326(self):
        self._assert_gml_lon_lat_ring(
            self._get_in_degrees("EPSG:4326", REQUEST="GetFeature")
        )

    def test_get_feature_gml_in_epsg_4326_urn_is_lat_lon(self):
        body = self._get_in_degrees("urn:ogc:def:crs:EPSG::4326", REQUEST="GetFeature")
        self._assert_coordinates(
            gml_values(GML_POS_LIST, body),
            [v for point in VILLARD_SQUARE_LON_LAT.coords[0] for v in reversed(point)],
        )

    def test_get_feature_filters_by_city_code(self):
        other_city = City.objects.create(
            name="Rillieux-la-Pape", code="69286", geometry=VILLARD_SQUARE
        )
        Tile.objects.create(
            geometry=VILLARD_SQUARE,
            plantability_indice=1.0,
            plantability_normalized_indice=2,
            city=other_city,
        )
        params = {
            "SERVICE": "WFS",
            "VERSION": "2.0.0",
            "REQUEST": "GetFeature",
            "TYPENAMES": "plantability",
            "OUTPUTFORMAT": "geojson",
        }

        unfiltered = b"".join(self.client.get(WFS_URL, params).streaming_content)
        filtered = b"".join(
            self.client.get(WFS_URL, {**params, "city_code": "69286"}).streaming_content
        )

        self.assertIn(b"Villard-de-Lans", unfiltered)
        self.assertIn(b"Rillieux-la-Pape", filtered)
        self.assertNotIn(b"Villard-de-Lans", filtered)


class VegestrateWFSViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.vegestrate = Vegestrate.objects.create(
            geometry=VILLARD_SQUARE,
            strate="arborescent",
            surface=120.5,
        )

    def test_get_capabilities_status(self):
        response = self.client.get(
            WFS_URL,
            {"SERVICE": "WFS", "REQUEST": "GetCapabilities"},
        )
        self.assertEqual(response.status_code, 200)

    def test_get_capabilities_contains_service_title(self):
        response = self.client.get(
            WFS_URL,
            {"SERVICE": "WFS", "REQUEST": "GetCapabilities"},
        )
        self.assertIn(b"vegestrate", response.content)

    def test_describe_feature_type_exposes_fields(self):
        response = self.client.get(
            WFS_URL,
            {
                "SERVICE": "WFS",
                "VERSION": "2.0.0",
                "REQUEST": "DescribeFeatureType",
                "TYPENAMES": "vegestrate",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"strate", response.content)
        self.assertIn(b"surface", response.content)

    def test_get_feature_status(self):
        response = self.client.get(
            WFS_URL,
            {
                "SERVICE": "WFS",
                "VERSION": "2.0.0",
                "REQUEST": "GetFeature",
                "TYPENAMES": "vegestrate",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_get_feature_returns_vegestrate(self):
        response = self.client.get(
            WFS_URL,
            {
                "SERVICE": "WFS",
                "VERSION": "2.0.0",
                "REQUEST": "GetFeature",
                "TYPENAMES": "vegestrate",
            },
        )
        body = b"".join(response.streaming_content)
        self.assertIn(b"arborescent", body)

    def test_get_feature_without_data(self):
        Vegestrate.objects.all().delete()
        response = self.client.get(
            WFS_URL,
            {
                "SERVICE": "WFS",
                "VERSION": "2.0.0",
                "REQUEST": "GetFeature",
                "TYPENAMES": "vegestrate",
            },
        )
        self.assertEqual(response.status_code, 200)
        body = b"".join(response.streaming_content)
        self.assertIn(b'numberReturned="0"', body)
