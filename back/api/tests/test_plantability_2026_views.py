import tempfile
from pathlib import Path

import mercantile
import numpy as np

from django.test import TestCase
from django.urls import reverse

from api.tests.test_hourly_raster_views import (
    RASTER_LAT_MAX,
    RASTER_LAT_MIN,
    RASTER_LNG_MAX,
    RASTER_LNG_MIN,
    decoded_values,
)
from iarbre_data.management.commands.populate import Command as PopulateCommand
from plantability.constants import BLOCKED_SCORE, PLANTABILITY_NORMALIZED

NODATA = -9999
SCORES = [BLOCKED_SCORE, -5, -2, -1.9, -0.75, 0.1, 0.2, 2.5, 3, NODATA]


class Plantability2026TileViewTest(TestCase):
    def setUp(self):
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        self.media_root = tmpdir.name
        tile = mercantile.tile(
            (RASTER_LNG_MIN + RASTER_LNG_MAX) / 2,
            (RASTER_LAT_MIN + RASTER_LAT_MAX) / 2,
            13,
        )
        self.tile_url = reverse(
            "plantability-2026-tile", kwargs={"z": tile.z, "x": tile.x, "y": tile.y}
        )

    def write(self, grid, scores):
        data = np.tile(np.array(scores, dtype=np.float32), (1, 10, 10))
        PopulateCommand._write_test_raster(
            Path(self.media_root)
            / "rasters/plantability_2026"
            / f"plantability_2026_villeurbanne_{grid}m.tif",
            data,
            NODATA,
        )

    def get(self, url=None, **params):
        with self.settings(MEDIA_ROOT=self.media_root):
            return self.client.get(url or self.tile_url, params)

    def test_scores_are_classified_like_production(self):
        self.write(5, SCORES)
        response = self.get(grid=5)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "image/png")
        self.assertEqual(decoded_values(response), set(PLANTABILITY_NORMALIZED))

    def test_threshold_value_falls_in_lower_class(self):
        self.write(5, [-2])
        self.assertEqual(decoded_values(self.get(grid=5)), {2})
        self.write(5, [2.5])
        self.assertEqual(decoded_values(self.get(grid=5)), {8})

    def test_blocked_score_is_transparent(self):
        self.write(5, [BLOCKED_SCORE])
        self.assertEqual(decoded_values(self.get(grid=5)), set())
        self.write(5, [-5])
        self.assertEqual(decoded_values(self.get(grid=5)), {0})

    def test_nodata_and_outside_tiles_are_transparent(self):
        self.write(5, [NODATA])
        self.assertEqual(decoded_values(self.get(grid=5)), set())
        self.write(5, SCORES)
        outside_url = reverse("plantability-2026-tile", kwargs={"z": 1, "x": 0, "y": 0})
        self.assertEqual(decoded_values(self.get(outside_url, grid=5)), set())

    def test_grid_switches_raster(self):
        self.write(5, [-1.9])
        self.write(1, [3])
        self.assertEqual(decoded_values(self.get(grid=1)), {10})

    def test_invalid_grid_returns_400(self):
        self.write(5, SCORES)
        self.assertEqual(self.get(grid=10).status_code, 400)

    def test_missing_raster_returns_404(self):
        self.assertEqual(self.get(grid=5).status_code, 404)

    def test_tiles_are_not_cached(self):
        self.write(5, [-1.9])
        response = self.get(grid=5)
        self.assertNotIn("max-age=86400", response.get("Cache-Control", ""))
        self.assertEqual(decoded_values(response), {4})
        self.write(5, [3])
        self.assertEqual(decoded_values(self.get(grid=5)), {10})
