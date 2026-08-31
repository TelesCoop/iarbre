from django.test import SimpleTestCase
from rest_framework.test import APISimpleTestCase
from django.urls import reverse

from api.utils.pdf_export import store_export_scope, get_export_scope


class ExportScopeStoreTest(SimpleTestCase):
    def test_store_and_get_roundtrip(self):
        scope = {"scale": "commune", "city_code": "69123"}
        token = store_export_scope(scope)
        self.assertTrue(token)
        self.assertEqual(get_export_scope(token), scope)

    def test_get_unknown_token_returns_none(self):
        self.assertIsNone(get_export_scope("does-not-exist"))


class ExportScopeViewTest(APISimpleTestCase):
    def test_returns_stored_scope(self):
        token = store_export_scope({"scale": "metropole"})
        url = reverse("dashboard-export-scope", args=[token])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"scale": "metropole"})

    def test_unknown_token_returns_404(self):
        url = reverse("dashboard-export-scope", args=["nope"])
        self.assertEqual(self.client.get(url).status_code, 404)
