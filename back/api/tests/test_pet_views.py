import io
import tempfile

import mercantile
import numpy as np
from PIL import Image

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from api.views.raster_tile_views import NODATA_HEIGHT
from iarbre_data.management.commands.populate import Command as PopulateCommand

RASTER_LNG_MIN, RASTER_LNG_MAX = 5.52, 5.58
RASTER_LAT_MIN, RASTER_LAT_MAX = 45.04, 45.10


def pet_classes(response):
    pixels = np.asarray(Image.open(io.BytesIO(response.content))).reshape(-1, 4)
    opaque = pixels[pixels[:, 3] == 255].astype(float)
    values = opaque[:, 0] * 256 + opaque[:, 1] + opaque[:, 2] / 256 - 32768
    return set(values.tolist()) - {NODATA_HEIGHT}


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)
class PetTileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.tmpdir = tempfile.mkdtemp()
        with self.settings(MEDIA_ROOT=self.tmpdir):
            PopulateCommand()._create_test_pet_rasters()
        tile = mercantile.bounding_tile(
            RASTER_LNG_MIN, RASTER_LAT_MIN, RASTER_LNG_MAX, RASTER_LAT_MAX
        )
        self.tile_url = reverse(
            "pet-tile", kwargs={"z": tile.z, "x": tile.x, "y": tile.y}
        )

    def test_tile_inside_raster_returns_pet_classes(self):
        with self.settings(MEDIA_ROOT=self.tmpdir):
            response = self.client.get(self.tile_url, {"year": 2020, "hour": 16})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "image/png")
        self.assertEqual(pet_classes(response), {8})

    def test_year_switches_scenario(self):
        with self.settings(MEDIA_ROOT=self.tmpdir):
            response = self.client.get(self.tile_url, {"year": 2090, "hour": 16})
        self.assertEqual(pet_classes(response), {9})

    def test_tile_outside_raster_returns_empty_png(self):
        outside_url = reverse("pet-tile", kwargs={"z": 1, "x": 0, "y": 0})
        with self.settings(MEDIA_ROOT=self.tmpdir):
            response = self.client.get(outside_url, {"year": 2020, "hour": 16})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(pet_classes(response), set())

    def test_missing_raster_returns_404(self):
        with self.settings(MEDIA_ROOT=tempfile.mkdtemp()):
            response = self.client.get(self.tile_url, {"year": 2020, "hour": 16})
        self.assertEqual(response.status_code, 404)

    def test_invalid_hour_returns_400(self):
        with self.settings(MEDIA_ROOT=self.tmpdir):
            response = self.client.get(self.tile_url, {"year": 2020, "hour": 25})
        self.assertEqual(response.status_code, 400)
