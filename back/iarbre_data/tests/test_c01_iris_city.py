from iarbre_data.management.commands.c01_insert_cities_and_iris import (
    Command as c01_city_iris,
)
from django.test import TestCase
from iarbre_data.models import City, Iris
from iarbre_data.settings import BASE_DIR
import os
import shutil


def move_test_data() -> None:
    file_data_dir = os.path.join(BASE_DIR, "file_data")
    test_data_dir = os.path.join(BASE_DIR, "iarbre_data/tests/test_data")

    if not os.path.exists(file_data_dir) or not os.listdir(file_data_dir):
        os.makedirs(file_data_dir, exist_ok=True)

        if os.path.exists(test_data_dir):
            for file_name in os.listdir(test_data_dir):
                source_path = os.path.join(test_data_dir, file_name)
                destination_path = os.path.join(file_data_dir, file_name)

                if os.path.isfile(source_path):
                    shutil.copy(source_path, destination_path)


class C01CityIrisTestCase(TestCase):
    def setUp(self):
        self.command = c01_city_iris()
        move_test_data()
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
