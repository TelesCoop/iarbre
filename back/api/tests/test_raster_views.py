import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from heat.raster import hour_raster_path


class RasterDownloadFilenameTest(SimpleTestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        src = Path(self.media.name) / "rasters/WMS/PET_index_2020.tif"
        hour = hour_raster_path(src, 14)
        hour.parent.mkdir(parents=True)
        src.write_bytes(b"src")
        hour.write_bytes(b"hour")

    def _get(self, query=""):
        url = reverse("download-raster", kwargs={"file_key": "pet_index"})
        with override_settings(MEDIA_ROOT=self.media.name):
            return self.client.get(f"{url}{query}")

    def test_full_raster_named_2020(self):
        response = self._get()
        self.assertIn('filename="PET_index_2020.tif"', response["Content-Disposition"])

    @patch("api.views.raster_views.rasterio.open")
    def test_hour_raster_named_2020(self, mock_open):
        mock_open.return_value.__enter__.return_value = MagicMock(count=25)
        response = self._get("?hour=14")
        self.assertIn(
            'filename="PET_index_2020_h14.tif"', response["Content-Disposition"]
        )
