from django.test import TestCase
from django.core.management import call_command
from django.core.files.base import ContentFile
from iarbre_data.models import MVTTile


class CleanMVTFilesCommandTest(TestCase):
    def setUp(self):
        MVTTile.objects.create(
            geolevel="city",
            datatype="test1",
            zoom_level=10,
            tile_x=1,
            tile_y=1,
            mvt_file=ContentFile(b"test_data", name="test.mvt"),
        )
        MVTTile.objects.create(
            geolevel="lcz",
            datatype="test2",
            zoom_level=10,
            tile_x=2,
            tile_y=2,
            mvt_file=ContentFile(b"test_data", name="test.mvt"),
        )

    def test_clean_all_tiles(self):
        self.assertEqual(MVTTile.objects.count(), 2)
        call_command("clean_mvt_files")
        self.assertEqual(MVTTile.objects.count(), 0)

    def test_clean_specific_geolevel_and_datatype(self):
        self.assertEqual(MVTTile.objects.count(), 2)
        call_command("clean_mvt_files", "--geolevel=city", "--datatype=test1")
        self.assertEqual(MVTTile.objects.count(), 1)
        remaining = MVTTile.objects.first()
        self.assertEqual(remaining.geolevel, "lcz")
        self.assertEqual(remaining.datatype, "test2")

    def test_clean_nonexistent_tiles(self):
        call_command("clean_mvt_files", "--geolevel=nonexistent", "--datatype=fake")
        self.assertEqual(MVTTile.objects.count(), 2)
