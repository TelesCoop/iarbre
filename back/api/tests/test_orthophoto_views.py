from unittest.mock import patch, MagicMock

from django.test import TestCase, Client, override_settings
from django.urls import reverse

from api.views.orthophoto_views import WMS_BASE_URL, WMS_LAYER


# Disable cache during tests
@override_settings(
    CACHES={
        "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
        "orthophoto": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
    }
)
class OrthophotoTileViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def _get_url(self, z=14, x=8345, y=5765):
        return reverse("orthophoto-tile", kwargs={"z": z, "x": x, "y": y})

    @patch("api.views.orthophoto_views.requests.get")
    def test_passes_correct_wms_params(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = b"png"
        mock_response.headers = {"Content-Type": "image/png"}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        self.client.get(self._get_url(z=14, x=8345, y=5765))

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertEqual(call_args[0][0], WMS_BASE_URL)
        params = call_args[1]["params"]
        self.assertEqual(params["SERVICE"], "WMS")
        self.assertEqual(params["LAYERS"], WMS_LAYER)
        self.assertEqual(params["CRS"], "EPSG:3857")
        self.assertEqual(params["FORMAT"], "image/png")
        self.assertEqual(params["WIDTH"], 256)
        self.assertEqual(params["HEIGHT"], 256)
        self.assertEqual(params["TRANSPARENT"], "TRUE")
