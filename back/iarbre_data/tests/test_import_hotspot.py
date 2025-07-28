from django.test import TestCase
from django.contrib.gis.geos import Point
from iarbre_data.management.commands.import_hotspot import Command
from iarbre_data.models import HotSpot
from iarbre_data.factories import CityFactory


class ImportHotspotCommandTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test cities
        cls.test_city = CityFactory(code="69001", name="Lyon 1er")

    def setUp(self):
        self.command = Command()
        # Clean hotspot data before each test
        HotSpot.objects.all().delete()

    def test_extract_first_street_number_simple(self):
        result = self.command.extract_first_street_number("123 Rue de la Paix")
        self.assertEqual(result, "123 Rue de la Paix")

    def test_extract_first_street_number_with_comma(self):
        result = self.command.extract_first_street_number("43,45,47,49 Rue Victor Hugo")
        self.assertEqual(result, "43 Rue Victor Hugo")

    def test_extract_first_street_number_with_slash(self):
        result = self.command.extract_first_street_number("43/45/47 Avenue Jean Jaurès")
        self.assertEqual(result, "43 Avenue Jean Jaurès")

    def test_clean_address_with_postal_code(self):
        result = self.command.clean_address("123 Rue de la Paix 69001 Lyon")
        self.assertEqual(result, "123 Rue de la Paix 69001")

    def test_clean_address_without_postal_code(self):
        result = self.command.clean_address("123 Rue de la Paix Lyon")
        self.assertEqual(result, "123 Rue de la Paix Lyon")

    def test_clean_address_empty(self):
        result = self.command.clean_address("")
        self.assertEqual(result, "")

        result = self.command.clean_address(None)
        self.assertIsNone(result)

    def test_get_city_from_address_existing(self):
        city = self.command.get_city_from_address("123 Rue de la Paix 69001 Lyon 1er")
        self.assertEqual(city, self.test_city)

    def test_extract_city_name_from_address(self):
        """Test extracting city name from address string."""
        result = self.command.extract_city_name_from_address(
            "123 Rue de la Paix 69001 Lyon"
        )
        self.assertEqual(result, "Lyon")

    def test_create_or_update_hotspot_creation(self):
        """Test creating new hotspot."""
        geometry = Point(4.85, 45.75, srid=4326)
        description = {"type": "tree", "height": 10}
        city_name = "Lyon 1er"

        result = self.command.create_or_update_hotspot(
            geometry, description, city_name, self.test_city
        )
        self.assertTrue(result)

        # Verify hotspot was created
        self.assertEqual(HotSpot.objects.count(), 1)
        hotspot = HotSpot.objects.first()
        self.assertEqual(hotspot.city_name, city_name)
        self.assertEqual(hotspot.city, self.test_city)
        self.assertEqual(hotspot.description, description)

    def test_create_or_update_hotspot_update(self):
        """Test updating existing hotspot."""
        geometry = Point(4.85, 45.75, srid=4326)

        # Create initial hotspot
        initial_description = {"type": "tree", "height": 10}
        HotSpot.objects.create(
            geometry=geometry,
            description=initial_description,
            city_name="Lyon",
            city=self.test_city,
        )

        # Update with new description
        new_description = {"type": "tree", "height": 15}
        result = self.command.create_or_update_hotspot(
            geometry, new_description, "Lyon 1er", self.test_city
        )
        self.assertTrue(result)

        # Verify hotspot was updated, not duplicated
        self.assertEqual(HotSpot.objects.count(), 1)
        hotspot = HotSpot.objects.first()
        self.assertEqual(hotspot.description, new_description)
        self.assertEqual(hotspot.city_name, "Lyon 1er")
