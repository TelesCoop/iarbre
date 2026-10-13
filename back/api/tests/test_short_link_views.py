import json

from django.test import TestCase, Client


class ShortLinkViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def post(self, path):
        return self.client.post(
            "/api/short-links/",
            json.dumps({"path": path}),
            content_type="application/json",
        )

    def test_roundtrip_and_dedup(self):
        path = "/biosphere_functional_integrity/14/45.76000/4.83000?filters=0-12,87-100"
        code = self.post(path).json()["code"]
        self.assertLessEqual(len(code), 8)
        self.assertEqual(self.post(path).json()["code"], code)
        response = self.client.get(f"/api/short-links/{code}/")
        self.assertEqual(response.json()["path"], path)

    def test_rejects_external_path(self):
        for path in ["https://evil.com", "//evil.com", "", None]:
            self.assertEqual(self.post(path).status_code, 400)

    def test_unknown_code(self):
        self.assertEqual(self.client.get("/api/short-links/nope/").status_code, 404)
