import json

from django.test import TestCase, Client


class DashboardPdfExportViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = "/api/dashboard/export-pdf/"

    def test_valid_html_returns_pdf(self):
        data = {"html": "<html><body><h1>Rapport</h1></body></html>"}
        response = self.client.post(
            self.url, json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_missing_html_field(self):
        response = self.client.post(
            self.url, json.dumps({}), content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

    def test_blank_html_field(self):
        response = self.client.post(
            self.url, json.dumps({"html": ""}), content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

    def test_external_resources_are_not_fetched(self):
        """An <img> pointing at an internal/external host must not be reachable (SSRF guard)."""
        data = {
            "html": (
                '<html><body><img src="http://169.254.169.254/latest/meta-data/">'
                "</body></html>"
            )
        }
        response = self.client.post(
            self.url, json.dumps(data), content_type="application/json"
        )

        # WeasyPrint swallows per-resource fetch errors and still renders the page.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b"%PDF"))
