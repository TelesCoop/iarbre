from unittest.mock import patch, MagicMock

from django.test import TestCase, Client, override_settings
from django.urls import reverse

from api.utils.tile_math import tile_to_bbox
from api.views.orthophoto_views import WMS_BASE_URL, WMS_LAYER


# Disable cache during tests
@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
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

    @patch("api.views.orthophoto_views.requests.get")
    def test_wms_error_returns_404(self, mock_get):
        import requests as req

        mock_get.side_effect = req.ConnectionError("Connection refused")

        response = self.client.get(self._get_url())

        self.assertEqual(response.status_code, 404)

    @patch("api.views.orthophoto_views.requests.get")
    def test_wms_xml_error_returns_404(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = (
            b"<ServiceExceptionReport>error</ServiceExceptionReport>"
        )
        mock_response.headers = {"Content-Type": "application/xml"}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        response = self.client.get(self._get_url())

        self.assertEqual(response.status_code, 404)


class TileToBboxTest(TestCase):
    def test_tile_0_0_0_covers_world(self):
        bbox = tile_to_bbox(0, 0, 0)
        self.assertAlmostEqual(bbox[0], -20037508.34, places=0)
        self.assertAlmostEqual(bbox[2], 20037508.34, places=0)

    def test_lyon_tile_has_valid_bbox(self):
        # Tile 14/8345/5765 should be around Lyon (lat ~45.75, lon ~4.85)
        bbox = tile_to_bbox(14, 8345, 5765)
        # x should be around 540000 in EPSG:3857 (lon ~4.85°)
        self.assertGreater(bbox[0], 300000)
        self.assertLess(bbox[2], 600000)
        # y should be around 5740000 in EPSG:3857 (lat ~45.75°)
        self.assertGreater(bbox[1], 5700000)
        self.assertLess(bbox[3], 6000000)

    def test_bbox_has_correct_order(self):
        bbox = tile_to_bbox(10, 512, 360)
        # x_min < x_max, y_min < y_max
        self.assertLess(bbox[0], bbox[2])
        self.assertLess(bbox[1], bbox[3])

    def test_adjacent_tiles_share_edges(self):
        bbox_left = tile_to_bbox(10, 512, 360)
        bbox_right = tile_to_bbox(10, 513, 360)
        # Right edge of left tile == left edge of right tile
        self.assertAlmostEqual(bbox_left[2], bbox_right[0], places=2)

        bbox_top = tile_to_bbox(10, 512, 360)
        bbox_bottom = tile_to_bbox(10, 512, 361)
        # Bottom edge of top tile == top edge of bottom tile
        self.assertAlmostEqual(bbox_top[1], bbox_bottom[3], places=2)
