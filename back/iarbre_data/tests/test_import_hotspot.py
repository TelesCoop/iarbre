import os
import tempfile
import pandas as pd
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
        cls.lyon_5_city = CityFactory(code="69005", name="Lyon 5e")

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

    def test_extract_first_street_number_with_complex_pattern(self):
        result = self.command.extract_first_street_number(
            "121 A,B,C,D,E,F,G,H Rue de la République"
        )
        self.assertEqual(result, "121 Rue de la République")

    def test_extract_first_street_number_with_slash_and_comma(self):
        result = self.command.extract_first_street_number(
            "51,53,55 / 57,59,61,63 Avenue Maréchal Foch"
        )
        self.assertEqual(result, "51 / 57,59,61,63 Avenue Maréchal Foch")

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

    def test_clean_address_with_complex_numbers(self):
        result = self.command.clean_address("43,45,47,49 Rue Victor Hugo 69005 Lyon")
        self.assertEqual(result, "43 Rue Victor Hugo 69005")

    def test_get_city_from_address_existing(self):
        city = self.command.get_city_from_address("123 Rue de la Paix 69001 Lyon 1er")
        self.assertEqual(city, self.test_city)

    def test_get_city_from_address_non_existing(self):
        city = self.command.get_city_from_address(
            "123 Rue de la Paix 69999 UnknownCity"
        )
        self.assertIsNone(city)

    def test_get_city_from_address_no_postal_code(self):
        city = self.command.get_city_from_address("123 Rue de la Paix Lyon")
        self.assertIsNone(city)

    def test_extract_city_name_from_address(self):
        result = self.command.extract_city_name_from_address(
            "123 Rue de la Paix 69001 Lyon"
        )
        self.assertEqual(result, "Lyon")

    def test_extract_city_name_from_address_multiple_words(self):
        result = self.command.extract_city_name_from_address(
            "123 Rue de la Paix 69005 Lyon 5e Arrondissement"
        )
        self.assertEqual(result, "Lyon 5e Arrondissement")

    def test_extract_city_name_from_address_no_postal_code(self):
        result = self.command.extract_city_name_from_address("123 Rue de la Paix")
        self.assertIsNone(result)

    def test_find_address_column(self):
        df = pd.DataFrame(
            {
                "Name": ["Test"],
                "Adresse Complète": ["123 Rue de la Paix"],
                "Other": ["data"],
            }
        )

        result = self.command.find_address_column(df)
        self.assertEqual(result, "Adresse Complète")

    def test_find_address_column_case_insensitive(self):
        df = pd.DataFrame(
            {"Name": ["Test"], "ADRESSE": ["123 Rue de la Paix"], "Other": ["data"]}
        )

        result = self.command.find_address_column(df)
        self.assertEqual(result, "ADRESSE")

    def test_find_address_column_empty_values(self):
        df = pd.DataFrame({"Name": ["Test"], "Adresse": [pd.NA], "Other": ["data"]})

        result = self.command.find_address_column(df)
        self.assertIsNone(result)

    def test_get_full_address_with_commune(self):
        df = pd.DataFrame({"Adresse": ["123 Rue de la Paix"], "Commune": ["Lyon 5"]})
        row = df.iloc[0]

        result = self.command.get_full_address(row, "Adresse", df)
        self.assertEqual(result, "123 Rue de la Paix, 69005")

    def test_get_full_address_without_commune(self):
        df = pd.DataFrame({"Adresse": ["123 Rue de la Paix"], "Other": ["test"]})
        row = df.iloc[0]

        result = self.command.get_full_address(row, "Adresse", df)
        self.assertEqual(result, "123 Rue de la Paix")

    def test_get_full_address_lyon_arrondissement_conversion(self):
        df = pd.DataFrame({"Adresse": ["123 Rue de la Paix"], "Commune": ["Lyon 1"]})
        row = df.iloc[0]

        result = self.command.get_full_address(row, "Adresse", df)
        self.assertEqual(result, "123 Rue de la Paix, 69001")

    def test_get_additional_data_columns(self):
        df = pd.DataFrame(
            {
                "Name": ["Test"],
                "Adresse": ["123 Rue de la Paix"],
                "Type": ["Tree"],
                "Height": [10],
                "Empty": [pd.NA],
            }
        )

        result = self.command.get_additional_data_columns(df, "Adresse")
        expected = {"Type": "Type", "Height": "Height"}
        self.assertEqual(result, expected)

    def test_build_description(self):
        row = pd.Series(
            {
                "Adresse": "123 Rue de la Paix",
                "Type": "Tree",
                "Height": 10,
                "Notes": "Test notes",
            }
        )
        additional_data = {"Type": "Type", "Height": "Height", "Notes": "Notes"}

        result = self.command.build_description("Sheet1", row, additional_data)
        expected = {
            "sheet": "Sheet1",
            "Type": "Tree",
            "Height": 10,
            "Notes": "Test notes",
        }
        self.assertEqual(result, expected)

    def test_create_or_update_hotspot_creation(self):
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

    def test_process_sheet_no_address_column(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            df = pd.DataFrame({"Name": ["Test"], "Type": ["Tree"]})
            df.to_excel(tmp_file.name, sheet_name="Sheet1", index=False)

            result = self.command.process_sheet(tmp_file.name, "Sheet1")
            self.assertEqual(result, 0)

            os.unlink(tmp_file.name)

    def test_hotspot_model_fields(self):
        geometry = Point(4.85, 45.75, srid=4326)
        description = {
            "type": "tree",
            "height": 10,
            "species": "Oak",
            "notes": "Large tree near park",
        }
        city_name = "Lyon 1er"

        hotspot = HotSpot.objects.create(
            geometry=geometry,
            description=description,
            city_name=city_name,
            city=self.test_city,
        )

        self.assertEqual(hotspot.geometry, geometry)
        self.assertEqual(hotspot.description, description)
        self.assertEqual(hotspot.city_name, city_name)
        self.assertEqual(hotspot.city, self.test_city)
        self.assertEqual(hotspot.description["species"], "Oak")
        self.assertEqual(hotspot.description["notes"], "Large tree near park")
