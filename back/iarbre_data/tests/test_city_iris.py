from django.test import TestCase
from django.contrib.gis.geos import Polygon
from iarbre_data.models import City, Iris


class CityIrisTestCase(TestCase):
    def setUp(self):
        self.city = City.objects.create(
            geometry=Polygon(((0, 0), (1, 1), (1, 0), (0, 0))),
            code="CITY123",
            name="Test City",
        )

        self.iris = Iris.objects.create(
            geometry=Polygon(((0, 0), (1, 1), (1, 0), (0, 0))),
            code="IRIS123",
            name="Test IRIS",
            city=self.city,
        )

    def test_city_creation(self):
        self.assertEqual(self.city.name, "Test City")
        self.assertEqual(self.city.code, "CITY123")
        self.assertFalse(self.city.tiles_generated)
        self.assertFalse(self.city.tiles_computed)
        self.assertEqual(str(self.city), "CITY name: Test City")

    def test_iris_creation(self):
        self.assertEqual(self.iris.name, "Test IRIS")
        self.assertEqual(self.iris.code, "IRIS123")
        self.assertEqual(self.iris.city, self.city)
        self.assertEqual(str(self.iris), "IRIS code: IRIS123")
