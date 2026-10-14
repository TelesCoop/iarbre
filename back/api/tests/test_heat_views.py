import io
from unittest.mock import patch

import numpy as np
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from PIL import Image

from api.constants import SHADOW_COLOR


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)
class HeatTileClassesFilterTest(SimpleTestCase):
    def _get_rgba(self, data, query):
        url = reverse("retrieve-heat-tile", kwargs={"z": 14, "x": 8345, "y": 5765})
        with (
            patch("api.views.heat_views.Path.exists", return_value=True),
            patch("api.views.heat_views.is_up_to_date", return_value=True),
            patch(
                "api.views.heat_views.HeatTileView._read_tile", return_value=(data, 0)
            ),
        ):
            response = self.client.get(f"{url}?{query}")
        self.assertEqual(response.status_code, 200)
        return np.array(Image.open(io.BytesIO(response.content)))[0]

    def _get_pixels(self, data, query):
        return self._get_rgba(data, query)[:, 3]

    def test_without_classes_shows_everything(self):
        data = np.array([[5, 6, 7, 8, 9]], dtype=np.uint8)
        alpha = self._get_pixels(data, "mode=pet_index&hour=14")
        self.assertEqual(alpha.tolist(), [255] * 5)

    def test_empty_classes_hides_everything(self):
        data = np.array([[5, 6, 7]], dtype=np.uint8)
        alpha = self._get_pixels(data, "mode=pet_index&hour=14&classes=")
        self.assertEqual(alpha.tolist(), [0, 0, 0])

    def test_shadow_shades_only_non_sunlit_pixels(self):
        data = np.array([[1.0, 0.03, 0.5]], dtype=np.float32)
        rgba = self._get_rgba(data, "mode=shadow&hour=14")
        self.assertEqual(
            rgba.tolist(), [[0, 0, 0, 0], list(SHADOW_COLOR), list(SHADOW_COLOR)]
        )

    def test_invalid_classes_returns_400(self):
        url = reverse("retrieve-heat-tile", kwargs={"z": 14, "x": 8345, "y": 5765})
        response = self.client.get(f"{url}?mode=pet_index&hour=14&classes=a")
        self.assertEqual(response.status_code, 400)
