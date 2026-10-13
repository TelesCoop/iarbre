import json

from django.core.cache import cache
from django.test import TestCase, Client, override_settings
from rest_framework.throttling import AnonRateThrottle


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
class ShortLinkViewTest(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()

    def post(self, path):
        return self.client.post(
            "/api/short-links/",
            json.dumps({"path": path}),
            content_type="application/json",
        )

    def test_roundtrip_and_dedup(self):
        path = "/biosphere_functional_integrity/14/45.76000/4.83000?filters=0-12,87-100"
        created = self.post(path)
        self.assertEqual(created.status_code, 201)
        code = created.json()["code"]
        self.assertLessEqual(len(code), 8)
        existing = self.post(path)
        self.assertEqual(existing.status_code, 200)
        self.assertEqual(existing.json()["code"], code)
        response = self.client.get(f"/api/short-links/{code}/")
        self.assertEqual(response.json()["path"], path)

    def test_rejects_external_path(self):
        for path in ["https://evil.com", "//evil.com", "", None]:
            self.assertEqual(self.post(path).status_code, 400)

    def test_throttles_anonymous_creation(self):
        limit = AnonRateThrottle().num_requests
        statuses = [
            self.post(f"/plantability/{i}").status_code for i in range(limit + 1)
        ]
        self.assertEqual(statuses, [201] * limit + [429])

    def test_unknown_code(self):
        self.assertEqual(self.client.get("/api/short-links/nope/").status_code, 404)
