"""Split between the public API (``/api/v1/``) and the internal one (``/api/app/``)."""

import shutil
import tempfile

from django.core.cache import cache
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import Resolver404, resolve, reverse

from api.tests.test_wms_views import _write_test_raster

PUBLIC_NAMES = {
    "retrieve-tile": ["tile", "plantability", 13, 4202, 2924],
    "vegetation-height-tile": [13, 4202, 2924],
    "vegetation-height-at-point": [],
    "scores-in-polygon": ["plantability"],
    "biosphere-land-cover-at-point": [],
    "dashboard": [],
    "dashboard-in-polygon": [],
    "city-list": [],
    "iris-list": [],
    "city-boundaries": [],
    "qpv-list": [],
    "public-buildings-list": [],
    "wfs": [],
    "wms": [],
    "download-raster": ["plantability"],
    "metadata": [],
    "schema": [],
    "swagger-ui": [],
}

APP_NAMES = {
    "pet-tile": [13, 4202, 2924],
    "shadow-tile": [13, 4202, 2924],
    "orthophoto-tile": [13, 4202, 2924],
    "retrieve-tile-details": ["plantability", 1],
    "dashboard-export-scope": ["token"],
    "dashboard-export-pdf": [],
    "create-feedback": [],
    "create-short-link": [],
    "retrieve-short-link": ["code"],
}


class UrlSplitTest(SimpleTestCase):
    def test_public_routes_are_under_v1(self):
        for name, args in PUBLIC_NAMES.items():
            with self.subTest(name=name):
                self.assertTrue(reverse(name, args=args).startswith("/api/v1/"))

    def test_app_routes_are_under_app(self):
        for name, args in APP_NAMES.items():
            with self.subTest(name=name):
                self.assertTrue(reverse(name, args=args).startswith("/api/app/"))

    def test_app_routes_are_not_public(self):
        for path in [
            "/api/v1/feedback/",
            "/api/v1/short-links/",
            "/api/v1/dashboard/export-pdf/",
            "/api/v1/orthophoto/13/4202/2924.png",
            "/api/v1/tiles/pet/13/4202/2924.png",
        ]:
            with self.subTest(path=path), self.assertRaises(Resolver404):
                resolve(path)

    def test_unversioned_routes_are_gone(self):
        for path in ["/api/cities/", "/api/dashboard/", "/api/feedback/"]:
            with self.subTest(path=path), self.assertRaises(Resolver404):
                resolve(path)

    def test_health_check_stays_unversioned(self):
        self.assertEqual(reverse("health-check"), "/api/health-check/")


class LegacyAliasTest(TestCase):
    """URLs published before ``v1/`` keep working, without redirect."""

    def setUp(self):
        self._media_dir = tempfile.mkdtemp()
        _write_test_raster(self._media_dir)
        self._override = override_settings(MEDIA_ROOT=self._media_dir)
        self._override.enable()
        cache.clear()

    def tearDown(self):
        self._override.disable()
        shutil.rmtree(self._media_dir, ignore_errors=True)
        cache.clear()

    def test_legacy_wms_advertises_legacy_url(self):
        params = {"SERVICE": "WMS", "VERSION": "1.3.0", "REQUEST": "GetCapabilities"}
        self.client.get("/api/v1/wms/", params)
        response = self.client.get("/api/wms/", params)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'href="http://testserver/api/wms/"', response.content)
        self.assertNotIn(b"/api/v1/wms/", response.content)

    def test_legacy_wfs_get_capabilities(self):
        response = self.client.get(
            "/api/wfs/", {"SERVICE": "WFS", "REQUEST": "GetCapabilities"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"IArbre WFS", response.content)

    def test_legacy_raster_download_resolves(self):
        match = resolve("/api/rasters/plantability/")
        self.assertEqual(match.func.view_class.__name__, "RasterDownloadView")
