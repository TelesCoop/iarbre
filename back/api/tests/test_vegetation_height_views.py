import io
import tempfile

import mercantile
import numpy as np
from PIL import Image

from django.test import Client, TestCase
from django.urls import reverse

from iarbre_data.management.commands.populate import Command as PopulateCommand

RASTER_LNG_MIN, RASTER_LNG_MAX = 5.52, 5.58
RASTER_LAT_MIN, RASTER_LAT_MAX = 45.04, 45.10
RASTER_HEIGHT = 12


class VegetationHeightTileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.tmpdir = tempfile.mkdtemp()
        with self.settings(MEDIA_ROOT=self.tmpdir):
            PopulateCommand()._create_test_raster()
        tile = mercantile.bounding_tile(
            RASTER_LNG_MIN, RASTER_LAT_MIN, RASTER_LNG_MAX, RASTER_LAT_MAX
        )
        self.tile_url = reverse(
            "vegetation-height-tile", kwargs={"z": tile.z, "x": tile.x, "y": tile.y}
        )

    def test_tile_inside_raster_returns_png(self):
        with self.settings(MEDIA_ROOT=self.tmpdir):
            response = self.client.get(self.tile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "image/png")

    def test_kind_raw_encodes_height(self):
        with self.settings(MEDIA_ROOT=self.tmpdir):
            response = self.client.get(self.tile_url, {"kind": "raw"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "image/png")

        img = Image.open(io.BytesIO(response.content))
        pixels = np.asarray(img).reshape(-1, 4)
        opaque = pixels[pixels[:, 3] == 255]
        self.assertTrue(len(opaque))
        heights = (
            opaque[:, 0].astype(float) * 256
            + opaque[:, 1]
            + opaque[:, 2].astype(float) / 256
            - 32768
        )
        # The test raster is uniformly RASTER_HEIGHT metres.
        self.assertIn(RASTER_HEIGHT, heights)

    def test_tile_outside_raster_returns_empty_png(self):
        outside_url = reverse("vegetation-height-tile", kwargs={"z": 1, "x": 0, "y": 0})
        with self.settings(MEDIA_ROOT=self.tmpdir):
            response = self.client.get(outside_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "image/png")

    def test_missing_raster_returns_404(self):
        with self.settings(MEDIA_ROOT=tempfile.mkdtemp()):
            response = self.client.get(self.tile_url)
        self.assertEqual(response.status_code, 404)


class VegetationHeightAtPointViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("vegetation-height-at-point")
        self.tmpdir = tempfile.mkdtemp()
        with self.settings(MEDIA_ROOT=self.tmpdir):
            PopulateCommand()._create_test_raster()

    def test_missing_lat_returns_400(self):
        response = self.client.get(self.url, {"lng": "5.55"})
        self.assertEqual(response.status_code, 400)

    def test_missing_lng_returns_400(self):
        response = self.client.get(self.url, {"lat": "45.07"})
        self.assertEqual(response.status_code, 400)

    def test_invalid_lat_returns_400(self):
        response = self.client.get(self.url, {"lat": "abc", "lng": "5.55"})
        self.assertEqual(response.status_code, 400)

    def test_invalid_lng_returns_400(self):
        response = self.client.get(self.url, {"lat": "45.07", "lng": "xyz"})
        self.assertEqual(response.status_code, 400)

    def test_missing_raster_returns_404(self):
        with self.settings(MEDIA_ROOT=tempfile.mkdtemp()):
            response = self.client.get(self.url, {"lat": "45.07", "lng": "5.55"})
        self.assertEqual(response.status_code, 404)

    def test_point_inside_raster_returns_height(self):
        with self.settings(MEDIA_ROOT=self.tmpdir):
            response = self.client.get(self.url, {"lat": "45.07", "lng": "5.55"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["height"], RASTER_HEIGHT)

    def test_point_outside_raster_returns_null_height(self):
        with self.settings(MEDIA_ROOT=self.tmpdir):
            response = self.client.get(self.url, {"lat": "0.0", "lng": "0.0"})
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["height"])
