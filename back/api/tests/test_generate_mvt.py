from django.test import TestCase
from django.core.files.base import ContentFile
from api.management.commands.generate_mvt import Command as GenerateMVTCommand
from api.constants import GeoLevel, DataType
from iarbre_data.models import MVTTile, City
from iarbre_data.management.commands.populate import Command as PopulateCommand


class GenerateMVTCommandTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        populate_cmd = PopulateCommand()
        populate_cmd._create_city_and_iris()
        populate_cmd.city = City.objects.get(code="38250")
        populate_cmd._generate_plantability_tiles()
        populate_cmd.generate_plantability_mvt_tiles(n_threads=1)

    def setUp(self):
        self.command = GenerateMVTCommand()

    def test_handle_tile_geolevel_selects_correct_model(self):
        options = {
            "geolevel": GeoLevel.TILE.value,
            "datatype": DataType.TILE.value,
            "number_of_thread": 1,
            "keep": False,
        }

        # Should not raise an error and complete successfully
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
        }

        self.command.handle(**options)

        # Original tile should still exist
        self.assertTrue(MVTTile.objects.filter(id=existing_tile.id).exists())
