import json

from django.test import Client, TestCase

from api.constants import WMS_LAYERS

WMS_URL = "/api/wms/"

_LAYER_NAME = next(iter(WMS_LAYERS))


class WMSCapabilitiesTest(TestCase):
    def setUp(self):
        self.client = Client()

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

    def test_get_capabilities_contains_layer_name(self):
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


class WMSGetLayersTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_layers_status(self):
        response = self.client.get(WMS_URL, {"REQUEST": "GetLayers"})
        self.assertEqual(response.status_code, 200)

    def test_get_layers_returns_list(self):
        response = self.client.get(WMS_URL, {"REQUEST": "GetLayers"})
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_get_layers_contains_known_layer(self):
        response = self.client.get(WMS_URL, {"REQUEST": "GetLayers"})
        data = json.loads(response.content)
        names = [entry["name"] for entry in data]
        self.assertIn(_LAYER_NAME, names)


class WMSGetMapTest(TestCase):
    def setUp(self):
        self.client = Client()
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
