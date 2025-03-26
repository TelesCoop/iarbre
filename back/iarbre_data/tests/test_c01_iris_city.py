from iarbre_data.management.commands.c01_insert_cities_and_iris import (
    Command as c01_city_iris,
)
from django.test import TestCase
from iarbre_data.models import City, Iris
from iarbre_data.settings import BASE_DIR


class C01CityIrisTestCase(TestCase):
    def setUp(self):
        self.command = c01_city_iris()
        data = str(BASE_DIR) + "/file_data/communes_gl_2025.geojson"
        self.command._insert_cities(data)

    def test_city_insertion(self):
        qs = City.objects.all()
        self.assertTrue(len(qs) > 0)

    def test_iris_insertion(self):
        qs = City.objects.first()
        self.command._insert_iris([qs])
        qs_iris = Iris.objects.all()
        self.assertNotEquals(len(qs_iris), 0)
