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
TERRARIUM_PRECISION = 1 / 256


def decoded_values(response):
    pixels = np.asarray(Image.open(io.BytesIO(response.content))).reshape(-1, 4)
    opaque = pixels[pixels[:, 3] == 255].astype(float)
    values = opaque[:, 0] * 256 + opaque[:, 1] + opaque[:, 2] / 256 - 32768
    return set(values.tolist()) - {NODATA_HEIGHT}


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)
class HourlyRasterTileViewTestCase(TestCase):
    url_name = None

    def setUp(self):
        self.client = Client()
        self.tmpdir = tempfile.mkdtemp()
        with self.settings(MEDIA_ROOT=self.tmpdir):
            PopulateCommand()._create_test_hourly_rasters()
        tile = mercantile.bounding_tile(
            RASTER_LNG_MIN, RASTER_LAT_MIN, RASTER_LNG_MAX, RASTER_LAT_MAX
        )
        self.tile_url = reverse(
            self.url_name, kwargs={"z": tile.z, "x": tile.x, "y": tile.y}
        )

    def get(self, url=None, media_root=None, **params):
        with self.settings(MEDIA_ROOT=media_root or self.tmpdir):
            return self.client.get(url or self.tile_url, params)


class PetTileViewTest(HourlyRasterTileViewTestCase):
    url_name = "pet-tile"

    def test_tile_inside_raster_returns_pet_classes(self):
        response = self.get(year=2020, hour=16)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "image/png")
        self.assertEqual(decoded_values(response), {8})

    def test_year_switches_scenario(self):
        response = self.get(year=2090, hour=16)
        self.assertEqual(decoded_values(response), {9})

    def test_tile_outside_raster_returns_empty_png(self):
        outside_url = reverse(self.url_name, kwargs={"z": 1, "x": 0, "y": 0})
        response = self.get(outside_url, year=2020, hour=16)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(decoded_values(response), set())

    def test_missing_raster_returns_404(self):
        response = self.get(media_root=tempfile.mkdtemp(), year=2020, hour=16)
        self.assertEqual(response.status_code, 404)

    def test_invalid_hour_returns_400(self):
        response = self.get(year=2020, hour=25)
        self.assertEqual(response.status_code, 400)


class ShadowTileViewTest(HourlyRasterTileViewTestCase):
    url_name = "shadow-tile"

    def test_tile_inside_raster_returns_tree_shade_without_year(self):
        response = self.get(hour=16)
        self.assertEqual(response.status_code, 200)
        (value,) = decoded_values(response)
        self.assertAlmostEqual(value, 0.03, delta=TERRARIUM_PRECISION)

    def test_invalid_hour_returns_400(self):
        response = self.get(hour=25)
        self.assertEqual(response.status_code, 400)
