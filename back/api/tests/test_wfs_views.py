from django.test import TestCase, Client
from django.contrib.gis.geos import Polygon
from iarbre_data.models import City, Iris, Tile

WFS_URL = "/api/wfs/plantability/"

VILLARD_SQUARE = Polygon(
    (
        (898233, 6441266),
        (903233, 6441266),
        (903233, 6446266),
        (898233, 6446266),
        (898233, 6441266),
    ),
    srid=2154,
)


class WFSViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.city = City.objects.create(
            name="Villard-de-Lans", code="38250", geometry=VILLARD_SQUARE
        )
        self.iris = Iris.objects.create(
            name="Villard-de-Lans IRIS", code="381234", geometry=VILLARD_SQUARE
        )
        self.tile = Tile.objects.create(
            geometry=VILLARD_SQUARE,
            plantability_indice=3.5,
            plantability_normalized_indice=7,
            city=self.city,
            iris=self.iris,
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
        self.assertIn(b"Plantability", response.content)

    def test_get_capabilities_contains_feature_type(self):
        response = self.client.get(
            WFS_URL,
            {"SERVICE": "WFS", "REQUEST": "GetCapabilities"},
        )
        self.assertIn(b"tile", response.content)

    def test_describe_feature_type_status(self):
        response = self.client.get(
            WFS_URL,
            {
                "SERVICE": "WFS",
                "VERSION": "2.0.0",
                "REQUEST": "DescribeFeatureType",
                "TYPENAMES": "tile",
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
                "TYPENAMES": "tile",
            },
        )
        self.assertIn(b"plantability_indice", response.content)
        self.assertIn(b"iris_name", response.content)
        self.assertIn(b"city_name", response.content)

    def test_get_feature_status(self):
        response = self.client.get(
            WFS_URL,
            {
                "SERVICE": "WFS",
                "VERSION": "2.0.0",
                "REQUEST": "GetFeature",
                "TYPENAMES": "tile",
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
                "TYPENAMES": "tile",
            },
        )
        body = b"".join(response.streaming_content)
        self.assertIn(b"Villard-de-Lans", body)

    def test_get_feature_without_data(self):
        Tile.objects.all().delete()
        response = self.client.get(
            WFS_URL,
            {
                "SERVICE": "WFS",
                "VERSION": "2.0.0",
                "REQUEST": "GetFeature",
                "TYPENAMES": "tile",
            },
        )
        self.assertEqual(response.status_code, 200)
        body = b"".join(response.streaming_content)
        self.assertIn(b'numberMatched="0"', body)
