from unittest import mock
from django.test import SimpleTestCase, override_settings
from rest_framework.test import APISimpleTestCase
from django.urls import reverse

from api.utils.pdf_export import store_export_scope, get_export_scope
from api.utils import pdf_renderer


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


class ExportPdfViewTest(APISimpleTestCase):
    @override_settings(PDF_EXPORT_FRONTEND_URL="")
    def test_returns_pdf(self):
        url = reverse("dashboard-export-pdf")
        with mock.patch(
            "api.views.dashboard_views.render_dashboard_pdf",
            return_value=b"%PDF-1.7 fake",
        ) as mock_render:
            response = self.client.post(
                url, {"scale": "commune", "city_code": "69123"}, format="json"
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.getvalue().startswith(b"%PDF"))
        self.assertEqual(mock_render.call_args.args[1], "http://testserver")

    def test_timeout_returns_504(self):
        url = reverse("dashboard-export-pdf")
        with mock.patch(
            "api.views.dashboard_views.render_dashboard_pdf",
            side_effect=pdf_renderer.PdfExportTimeout("slow"),
        ):
            response = self.client.post(url, {"scale": "metropole"}, format="json")
        self.assertEqual(response.status_code, 504)
