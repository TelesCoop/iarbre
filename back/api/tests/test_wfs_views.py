from django.test import TestCase, Client
from django.contrib.gis.geos import Polygon
from iarbre_data.settings import TARGET_PROJ
from iarbre_data.models import City, Tile, Vegestrate

WFS_URL = "/api/wfs/"

VILLARD_SQUARE = Polygon(
    (
        (898233, 6441266),
        (903233, 6441266),
        (903233, 6446266),
        (898233, 6446266),
        (898233, 6441266),
    ),
    srid=TARGET_PROJ,
)


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
