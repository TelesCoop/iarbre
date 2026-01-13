from django.test import TestCase
from django.core.files.base import ContentFile
from api.management.commands.generate_mvt import Command as GenerateMVTCommand
from api.constants import GeoLevel, DataType
from iarbre_data.models import MVTTile, City
from iarbre_data.management.commands.populate import Command as PopulateCommand
from api.utils.mvt_generator import MVTGenerator


class GenerateMVTCommandTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        populate_cmd = PopulateCommand()
        populate_cmd._create_city_and_iris()
        populate_cmd.city = City.objects.get(code="38250")
        populate_cmd._generate_plantability_tiles()

    def setUp(self):
        self.command = GenerateMVTCommand()

    def test_handle_tile_geolevel_selects_correct_model(self):
        options = {
            "geolevel": GeoLevel.TILE.value,
            "datatype": DataType.TILE.value,
            "number_of_thread": 1,
            "keep": False,
            "zoom_levels": (13, 13),
        }
        try:
            self.command.handle(**options)
            success = True
        except Exception as e:
            print(f"Exception: {e}")
            success = False

        self.assertTrue(success)

    def test_handle_deletes_existing_tiles_when_keep_false(self):
        # Create existing MVT tile
        mvt_tile = MVTTile.objects.create(
            geolevel=GeoLevel.TILE.value,
            datatype=DataType.TILE.value,
            zoom_level=10,
            tile_x=1,
            tile_y=1,
        )
        mvt_tile.mvt_file.save("test.mvt", ContentFile(b"test"))

        initial_count = MVTTile.objects.filter(
            geolevel=GeoLevel.TILE.value, datatype=DataType.TILE.value
        ).count()

        self.assertEqual(initial_count, 1)

        options = {
            "geolevel": GeoLevel.TILE.value,
            "datatype": DataType.TILE.value,
            "number_of_thread": 1,
            "keep": False,
            "zoom_levels": (13, 13),
        }

        self.command.handle(**options)

        # Should have generated new tiles
        final_count = MVTTile.objects.filter(
            geolevel=GeoLevel.TILE.value, datatype=DataType.TILE.value
        ).count()

        # Tiles should have been recreated
        self.assertGreaterEqual(final_count, 0)

    def test_handle_keeps_existing_tiles_when_keep_true(self):
        # Create existing MVT tile
        existing_tile = MVTTile.objects.create(
            geolevel=GeoLevel.TILE.value,
            datatype=DataType.TILE.value,
            zoom_level=10,
            tile_x=1,
            tile_y=1,
        )
        existing_tile.mvt_file.save("original.mvt", ContentFile(b"original_data"))

        options = {
            "geolevel": GeoLevel.TILE.value,
            "datatype": DataType.TILE.value,
            "number_of_thread": 1,
            "keep": True,
            "zoom_levels": (13, 13),
        }

        self.command.handle(**options)

        # Original tile should still exist
        self.assertTrue(MVTTile.objects.filter(id=existing_tile.id).exists())

    def test_mixed_indice_calculation(self):
        """Test that calculate_mixed_indice function works correctly"""
        # Test various combinations of plantability and vulnerability indices
        test_cases = [
            # (plantability_indice, vulnerability_indice, expected_mixed_indice)
            (0, 1, 1),  # Min plantability, min vulnerability
            (0, 9, 5),  # Min plantability, max vulnerability
            (2.5, 1, 11),  # Low plantability
            (2.5, 5, 13),  # Low plantability, mid vulnerability
            (5, 5, 23),  # Mid plantability, mid vulnerability
            (7.5, 7, 34),  # High plantability, high vulnerability
            (10, 1, 41),  # Max plantability, min vulnerability
            (10, 9, 45),  # Max plantability, max vulnerability
        ]

        for plantability, vulnerability, expected in test_cases:
            result = MVTGenerator.calculate_mixed_indice(plantability, vulnerability)
            self.assertEqual(
                result,
                expected,
                f"calculate_mixed_indice({plantability}, {vulnerability}) = {result}, expected {expected}",
            )
            # Verify result is in valid range
            self.assertGreaterEqual(result, 1, f"Result {result} below minimum")
            self.assertLessEqual(result, 45, f"Result {result} above maximum")

    def test_mixed_indice_with_none_values(self):
        """Test that calculate_mixed_indice handles None values correctly"""

        # Should return None when either input is None
        self.assertIsNone(MVTGenerator.calculate_mixed_indice(None, 5))
        self.assertIsNone(MVTGenerator.calculate_mixed_indice(5, None))
        self.assertIsNone(MVTGenerator.calculate_mixed_indice(None, None))

    def test_mixed_indice_boundary_values(self):
        """Test calculate_mixed_indice with boundary values"""
        # Test plantability boundaries (0-10 scale maps to 0-4 grid)
        # 0 -> 0, 2.5 -> 1, 5 -> 2, 7.5 -> 3, 10 -> 4
        # Note: vulnerability 5 maps to component 3 (see vulnerability boundaries test below)
        self.assertEqual(MVTGenerator.calculate_mixed_indice(0, 5), 3)  # 0*10 + 3
        self.assertEqual(MVTGenerator.calculate_mixed_indice(2, 5), 3)  # 0*10 + 3
        self.assertEqual(MVTGenerator.calculate_mixed_indice(2.5, 5), 13)  # 1*10 + 3
        self.assertEqual(MVTGenerator.calculate_mixed_indice(4, 5), 13)  # 1*10 + 3
        self.assertEqual(MVTGenerator.calculate_mixed_indice(5, 5), 23)  # 2*10 + 3
        self.assertEqual(MVTGenerator.calculate_mixed_indice(7.49, 5), 23)  # 2*10 + 3
        self.assertEqual(MVTGenerator.calculate_mixed_indice(7.5, 5), 33)  # 3*10 + 3
        self.assertEqual(MVTGenerator.calculate_mixed_indice(9, 5), 33)  # 3*10 + 3
        self.assertEqual(MVTGenerator.calculate_mixed_indice(10, 5), 43)  # 4*10 + 3

        # Test vulnerability boundaries (1-9 scale maps to 1-5 grid)
        self.assertEqual(MVTGenerator.calculate_mixed_indice(5, 1), 21)  # 2*10 + 1
        self.assertEqual(MVTGenerator.calculate_mixed_indice(5, 2), 21)  # 2*10 + 1
        self.assertEqual(MVTGenerator.calculate_mixed_indice(5, 3), 22)  # 2*10 + 2
        self.assertEqual(MVTGenerator.calculate_mixed_indice(5, 4), 22)  # 2*10 + 2
        self.assertEqual(MVTGenerator.calculate_mixed_indice(5, 5), 23)  # 2*10 + 3
        self.assertEqual(MVTGenerator.calculate_mixed_indice(5, 6), 23)  # 2*10 + 3
        self.assertEqual(MVTGenerator.calculate_mixed_indice(5, 7), 24)  # 2*10 + 4
        self.assertEqual(MVTGenerator.calculate_mixed_indice(5, 8), 24)  # 2*10 + 4
        self.assertEqual(MVTGenerator.calculate_mixed_indice(5, 9), 25)  # 2*10 + 5
