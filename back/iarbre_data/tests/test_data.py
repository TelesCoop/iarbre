from django.test import TestCase
from iarbre_data.models import Data
from django.contrib.gis.geos import Polygon


class DataTest(TestCase):
    def setUp(self):
        self.valid_geometry = Polygon(
            (
                (500000, 6500000),
                (500100, 6500000),
                (500100, 6500100),
                (500000, 6500100),
                (500000, 6500000),
            ),
            srid=2154,
        )
        self.data_instance = Data.objects.create(
            geometry=self.valid_geometry,
            metadata="Sample Metadata",
            factor="Plan d'eau",
        )

    def test_data_creation(self):
        self.assertEqual(self.data_instance.metadata, "Sample Metadata")
        self.assertEqual(self.data_instance.factor, "Plan d'eau")
        self.assertEqual(self.data_instance.geometry, self.valid_geometry)

    def test_invalid_geometry(self):
        """Test that invalid geometries raise an error"""
        with self.assertRaises(ValueError):
            Data.objects.create(
                geometry="InvalidGeometry", metadata="Meta", factor="Factor"
            )
