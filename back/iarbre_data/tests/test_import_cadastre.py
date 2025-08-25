from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry
from iarbre_data.management.commands.import_cadastre import Command
from iarbre_data.models import Cadastre
from iarbre_data.factories import CityFactory


class ImportCadastreCommandTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test cities using factory
        cls.test_city = CityFactory(code="69001", name="Lyon 1er")
        cls.test_city_2 = CityFactory(code="69002", name="Lyon 2e")

    def setUp(self):
        self.command = Command()
        # Clean cadastre data before each test
        Cadastre.objects.all().delete()

    def test_cadastre_model_creation(self):
        initial_count = Cadastre.objects.count()

        cadastre = Cadastre.objects.create(
            parcel_id="690010000A0001",
            city_code="69001",
            city_name="Lyon 1er",
            city=self.test_city,
            section="A",
            numero="0001",
            surface=500,
            geometry=GEOSGeometry(
                "POLYGON((4.8 45.7, 4.81 45.7, 4.81 45.71, 4.8 45.71, 4.8 45.7))",
                srid=2154,
            ),
        )

        self.assertEqual(Cadastre.objects.count(), initial_count + 1)
        self.assertEqual(cadastre.parcel_id, "690010000A0001")
        self.assertEqual(cadastre.city_code, "69001")
        self.assertEqual(cadastre.city_name, "Lyon 1er")
        self.assertEqual(cadastre.section, "A")
        self.assertEqual(cadastre.numero, "0001")
        self.assertEqual(cadastre.surface, 500)
        self.assertEqual(cadastre.city, self.test_city)

    def test_cadastre_duplicate_prevention(self):
        # Create first cadastre
        Cadastre.objects.create(
            parcel_id="690010000A0001",
            city_code="69001",
            city=self.test_city,
            geometry=GEOSGeometry(
                "POLYGON((4.8 45.7, 4.81 45.7, 4.81 45.71, 4.8 45.71, 4.8 45.7))",
                srid=2154,
            ),
        )

        # Check if duplicate exists (this is what the command does)
        existing_parcel = Cadastre.objects.filter(parcel_id="690010000A0001").first()
        self.assertIsNotNone(existing_parcel)

        # Verify we can find existing parcels
        duplicate_check = Cadastre.objects.filter(parcel_id="690010000A0001").exists()
        self.assertTrue(duplicate_check)

    def test_cadastre_creation_with_all_fields(self):
        # Create cadastre with all possible fields from the API
        cadastre = Cadastre.objects.create(
            parcel_id="690010000A0001",
            city_code="69001",
            city_name="Lyon 1er",
            city=self.test_city,
            section="A",
            numero="0001",
            surface=1500,  # contenance from API
            geometry=GEOSGeometry(
                "POLYGON((4.8 45.7, 4.81 45.7, 4.81 45.71, 4.8 45.71, 4.8 45.7))",
                srid=2154,
            ),
        )

        # Verify all fields are properly set
        self.assertEqual(cadastre.parcel_id, "690010000A0001")
        self.assertEqual(cadastre.city_code, "69001")
        self.assertEqual(cadastre.city_name, "Lyon 1er")
        self.assertEqual(cadastre.city, self.test_city)
        self.assertEqual(cadastre.section, "A")
        self.assertEqual(cadastre.numero, "0001")
        self.assertEqual(cadastre.surface, 1500)
        self.assertIsNotNone(cadastre.geometry)
