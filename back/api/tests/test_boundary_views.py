from django.contrib.gis.geos import Polygon
from django.test import Client, TestCase
from django.urls import reverse

from iarbre_data.models import City, Iris


class CityBoundaryViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        square = Polygon(((0, 0), (1, 0), (1, 1), (0, 1), (0, 0)), srid=2154)
        self.city = City.objects.create(geometry=square, code="69123", name="Lyon")

    def test_city_boundaries_returns_geojson(self):
        url = reverse("city-boundaries")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["type"], "FeatureCollection")
        self.assertGreater(len(data["features"]), 0)

    def test_city_boundary_features_have_properties(self):
        url = reverse("city-boundaries")
        response = self.client.get(url)

        data = response.json()
        feature = data["features"][0]
        self.assertIn("code", feature["properties"])
        self.assertIn("name", feature["properties"])
        self.assertEqual(feature["properties"]["code"], "69123")
        self.assertEqual(feature["properties"]["name"], "Lyon")


class IrisBoundaryViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        square = Polygon(((0, 0), (1, 0), (1, 1), (0, 1), (0, 0)), srid=2154)
        city = City.objects.create(geometry=square, code="69123", name="Lyon")
        self.iris = Iris.objects.create(
            geometry=square, code="691230101", name="Bellecour", city=city
        )

    def test_iris_boundaries_returns_geojson(self):
        url = reverse("iris-boundaries")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["type"], "FeatureCollection")
        self.assertGreater(len(data["features"]), 0)

    def test_iris_boundary_features_have_properties(self):
        url = reverse("iris-boundaries")
        response = self.client.get(url)

        data = response.json()
        feature = data["features"][0]
        self.assertIn("code", feature["properties"])
        self.assertIn("name", feature["properties"])
        self.assertEqual(feature["properties"]["code"], "691230101")
        self.assertEqual(feature["properties"]["name"], "Bellecour")
