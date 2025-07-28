from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry
from iarbre_data.management.commands.import_lcz import Command
from iarbre_data.models import Lcz
from iarbre_data.factories import CityFactory


class ImportLczCommandTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_city = CityFactory(code="69001", name="Lyon 1er")

    def setUp(self):
        self.command = Command()
        Lcz.objects.all().delete()

    def test_lcz_model_creation(self):
        initial_count = Lcz.objects.count()

        lcz = Lcz.objects.create(
            geometry=GEOSGeometry(
                "POLYGON((4.8 45.7, 4.81 45.7, 4.81 45.71, 4.8 45.71, 4.8 45.7))",
                srid=2154,
            ),
            map_geometry=GEOSGeometry(
                "POLYGON((4.8 45.7, 4.81 45.7, 4.81 45.71, 4.8 45.71, 4.8 45.7))",
                srid=3857,
            ),
            lcz_index="1",
            lcz_description="Compact high-rise",
            details={"hre": 0.5, "are": 0.3},
        )

        self.assertEqual(Lcz.objects.count(), initial_count + 1)
        self.assertEqual(lcz.lcz_index, "1")
        self.assertEqual(lcz.lcz_description, "Compact high-rise")
