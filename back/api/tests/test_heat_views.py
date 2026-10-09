import io
from unittest.mock import patch

import numpy as np
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from PIL import Image


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)
class HeatTileClassesFilterTest(SimpleTestCase):
    def _get_pixels(self, data, query):
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
        return np.array(Image.open(io.BytesIO(response.content)))[0, :, 3]

    def test_sun_exposure_hides_unselected_bins(self):
        data = np.array([[0.1, 0.3, 0.5, 0.7, 0.85, 0.95]], dtype=np.float32)
        alpha = self._get_pixels(data, "mode=sun_exposure&classes=1,4")
        self.assertEqual(alpha.tolist(), [0, 255, 0, 0, 255, 0])

    def test_without_classes_shows_everything(self):
        data = np.array([[0.1, 0.3, 0.5, 0.7, 0.85, 0.95]], dtype=np.float32)
        alpha = self._get_pixels(data, "mode=sun_exposure")
        self.assertEqual(alpha.tolist(), [255] * 6)

    def test_empty_classes_hides_everything(self):
        data = np.array([[5, 6, 7]], dtype=np.uint8)
        alpha = self._get_pixels(data, "mode=pet_index&hour=14&classes=")
        self.assertEqual(alpha.tolist(), [0, 0, 0])

    def test_pet_index_2090_uses_pet_colors(self):
        data = np.array([[5, 7, 9]], dtype=np.uint8)
        alpha = self._get_pixels(data, "mode=pet_index_2090&hour=14&classes=0,4")
        self.assertEqual(alpha.tolist(), [255, 0, 255])

    def test_invalid_classes_returns_400(self):
        url = reverse("retrieve-heat-tile", kwargs={"z": 14, "x": 8345, "y": 5765})
        response = self.client.get(f"{url}?mode=sun_exposure&classes=a")
        self.assertEqual(response.status_code, 400)
