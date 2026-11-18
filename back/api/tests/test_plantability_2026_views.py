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
from iarbre_data.data_config import FACTORS
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


class Plantability2026PointViewTest(TestCase):
    point = {
        "lng": (RASTER_LNG_MIN + RASTER_LNG_MAX) / 2,
        "lat": (RASTER_LAT_MIN + RASTER_LAT_MAX) / 2,
    }

    def setUp(self):
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        self.media_root = Path(tmpdir.name)
        self.url = reverse("plantability-2026-value")

    def write(self, grid, score, factors):
        folder = self.media_root / "rasters/plantability_2026"
        PopulateCommand._write_test_raster(
            folder / f"plantability_2026_villeurbanne_{grid}m.tif",
            np.full((1, 10, 10), score, dtype=np.float32),
            NODATA,
        )
        for factor in set(FACTORS) - {"QPV"}:
            PopulateCommand._write_test_raster(
                folder / f"factors_{grid}m" / f"{factor}.tif",
                np.full((1, 10, 10), factors.get(factor, 0), dtype=np.uint8),
                None,
            )

    def get(self, **params):
        with self.settings(MEDIA_ROOT=self.media_root):
            return self.client.get(self.url, params)

    def test_returns_score_class_and_top5_with_networks_grouped(self):
        self.write(
            1,
            3,
            {
                "Bâtiments": 100,
                "Rsx gaz": 40,
                "Rsx souterrains ERDF": 30,
                "Strate arborée": 20,
            },
        )
        response = self.get(grid=1, **self.point)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["plantabilityIndice"], 3)
        self.assertEqual(data["plantabilityNormalizedIndice"], 10)
        self.assertEqual(
            data["details"]["top5LandUse"],
            {"Bâtiments": 100, "Réseaux et infrastructures": 70, "Strate arborée": 20},
        )

    def test_blocked_point_is_class_zero_with_its_land_uses(self):
        self.write(5, BLOCKED_SCORE, {"Bâtiments": 100})
        data = self.get(grid=5, **self.point).json()
        self.assertEqual(data["plantabilityNormalizedIndice"], 0)
        self.assertEqual(data["details"]["top5LandUse"], {"Bâtiments": 100})

    def test_grid_switches_rasters(self):
        self.write(5, -1.9, {"Parkings": 50})
        self.write(1, 3, {"Strate arborée": 80})
        data = self.get(grid=5, **self.point).json()
        self.assertEqual(data["plantabilityNormalizedIndice"], 4)
        self.assertEqual(data["details"]["top5LandUse"], {"Parkings": 50})

    def test_point_outside_raster_or_on_nodata_returns_404(self):
        self.write(1, 3, {})
        self.assertEqual(self.get(grid=1, lat=0, lng=0).status_code, 404)
        self.write(1, NODATA, {})
        self.assertEqual(self.get(grid=1, **self.point).status_code, 404)

    def test_invalid_params_return_400(self):
        self.write(1, 3, {})
        self.assertEqual(self.get(grid=1, lat=45.07).status_code, 400)
        self.assertEqual(self.get(grid=10, **self.point).status_code, 400)
