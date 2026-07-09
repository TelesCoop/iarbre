import json
import shutil
import tempfile
from pathlib import Path

import numpy as np
import rasterio
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from rasterio.transform import from_bounds

WMS_URL = "/api/wms/"

_LAYER_STEM = "test_layer"
_LAYER_NAME = f"iarbre:{_LAYER_STEM}"


def _write_test_raster(media_root: str) -> None:
    """Create ``rasters/WMS/test_layer.tif`` so layer discovery has something to find.

    The raster is in EPSG:4326 and covers the BBOX used by the GetMap tests
    (lon 4.7-5.2, lat 45.5-46.0).
    """
    wms_dir = Path(media_root) / "rasters" / "WMS"
    wms_dir.mkdir(parents=True, exist_ok=True)
    width = height = 16
    transform = from_bounds(4.6, 45.4, 5.3, 46.1, width, height)
    data = np.arange(width * height, dtype=np.uint8).reshape(height, width)
    with rasterio.open(
        wms_dir / f"{_LAYER_STEM}.tif",
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype="uint8",
        crs="EPSG:4326",
        transform=transform,
        nodata=0,
    ) as dst:
        dst.write(data, 1)


class _WMSFixtureMixin:
    """Point MEDIA_ROOT at a temp dir holding a single test raster."""

    def setUp(self):
        self.client = Client()
        self._media_dir = tempfile.mkdtemp()
        _write_test_raster(self._media_dir)
        self._override = override_settings(MEDIA_ROOT=self._media_dir)
        self._override.enable()
        cache.clear()

    def tearDown(self):
        self._override.disable()
        shutil.rmtree(self._media_dir, ignore_errors=True)
        cache.clear()


class WMSCapabilitiesTest(_WMSFixtureMixin, TestCase):
    def test_get_capabilities_status(self):
        response = self.client.get(
            WMS_URL,
            {"SERVICE": "WMS", "VERSION": "1.3.0", "REQUEST": "GetCapabilities"},
        )
        self.assertEqual(response.status_code, 200)

    def test_get_capabilities_content_type(self):
        response = self.client.get(
            WMS_URL,
            {"SERVICE": "WMS", "VERSION": "1.3.0", "REQUEST": "GetCapabilities"},
        )
        self.assertIn("xml", response["content-type"])

    def test_get_capabilities_version_130_root_element(self):
        response = self.client.get(
            WMS_URL,
            {"SERVICE": "WMS", "VERSION": "1.3.0", "REQUEST": "GetCapabilities"},
        )
        self.assertIn(b"WMS_Capabilities", response.content)

    def test_get_capabilities_version_111_root_element(self):
        response = self.client.get(
            WMS_URL,
            {"SERVICE": "WMS", "VERSION": "1.1.1", "REQUEST": "GetCapabilities"},
        )
        self.assertIn(b"WMT_MS_Capabilities", response.content)

    def test_get_capabilities_contains_discovered_layer(self):
        response = self.client.get(
            WMS_URL,
            {"SERVICE": "WMS", "VERSION": "1.3.0", "REQUEST": "GetCapabilities"},
        )
        self.assertIn(_LAYER_NAME.encode(), response.content)

    def test_unsupported_request_returns_400(self):
        response = self.client.get(
            WMS_URL,
            {"SERVICE": "WMS", "REQUEST": "GetFeatureInfo"},
        )
        self.assertEqual(response.status_code, 400)


class WMSGetLayersTest(_WMSFixtureMixin, TestCase):
    def test_get_layers_status(self):
        response = self.client.get(WMS_URL, {"REQUEST": "GetLayers"})
        self.assertEqual(response.status_code, 200)

    def test_get_layers_returns_list(self):
        response = self.client.get(WMS_URL, {"REQUEST": "GetLayers"})
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_get_layers_contains_discovered_layer(self):
        response = self.client.get(WMS_URL, {"REQUEST": "GetLayers"})
        data = json.loads(response.content)
        names = [entry["name"] for entry in data]
        self.assertIn(_LAYER_NAME, names)

    def test_get_layers_empty_when_no_rasters(self):
        for tif in (Path(self._media_dir) / "rasters" / "WMS").glob("*.tif"):
            tif.unlink()
        response = self.client.get(WMS_URL, {"REQUEST": "GetLayers"})
        self.assertEqual(json.loads(response.content), [])


class WMSGetMapTest(_WMSFixtureMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.valid_params = {
            "SERVICE": "WMS",
            "VERSION": "1.3.0",
            "REQUEST": "GetMap",
            "LAYERS": _LAYER_NAME,
            "CRS": "EPSG:4326",
            "BBOX": "45.5,4.7,46.0,5.2",
            "WIDTH": "256",
            "HEIGHT": "256",
            "FORMAT": "image/png",
        }

    def test_valid_getmap_returns_png(self):
        response = self.client.get(WMS_URL, self.valid_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "image/png")

    def test_unknown_layer_returns_400(self):
        params = {**self.valid_params, "LAYERS": "iarbre:nonexistent"}
        response = self.client.get(WMS_URL, params)
        self.assertEqual(response.status_code, 400)

    def test_invalid_bbox_returns_400(self):
        params = {**self.valid_params, "BBOX": "not,a,valid,bbox"}
        response = self.client.get(WMS_URL, params)
        self.assertEqual(response.status_code, 400)

    def test_bbox_too_few_values_returns_400(self):
        params = {**self.valid_params, "BBOX": "45.5,4.7,46.0"}
        response = self.client.get(WMS_URL, params)
        self.assertEqual(response.status_code, 400)

    def test_invalid_width_returns_400(self):
        params = {**self.valid_params, "WIDTH": "abc"}
        response = self.client.get(WMS_URL, params)
        self.assertEqual(response.status_code, 400)

    def test_invalid_height_returns_400(self):
        params = {**self.valid_params, "HEIGHT": "abc"}
        response = self.client.get(WMS_URL, params)
        self.assertEqual(response.status_code, 400)

    def test_unsupported_format_returns_400(self):
        params = {**self.valid_params, "FORMAT": "image/tiff"}
        response = self.client.get(WMS_URL, params)
        self.assertEqual(response.status_code, 400)
