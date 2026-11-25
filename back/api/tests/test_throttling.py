from unittest import mock

from django.core.cache import caches
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from api.throttling import (
    PdfExportBurstThrottle,
    PdfExportSustainedThrottle,
    PolygonThrottle,
    WriteThrottle,
)


class ThrottleTestCase(APITestCase):
    def setUp(self):
        caches["throttle"].clear()

    def post_until_throttled(self, url, data, limit, **extra):
        """Post ``limit`` times, then once more; return the status codes."""
        return [
            self.client.post(url, data, format="json", **extra).status_code
            for _ in range(limit + 1)
        ]


class PdfExportThrottleTest(ThrottleTestCase):
    def test_rates(self):
        burst, sustained = PdfExportBurstThrottle(), PdfExportSustainedThrottle()
        self.assertEqual((burst.num_requests, burst.duration), (2, 60))
        self.assertEqual((sustained.num_requests, sustained.duration), (20, 3600))

    @mock.patch("api.views.dashboard.render_dashboard_pdf", return_value=b"%PDF")
    def test_burst_limit(self, _render):
        statuses = self.post_until_throttled(
            reverse("dashboard-export-pdf"), {"scale": "metropole"}, limit=2
        )
        self.assertEqual(statuses, [200, 200, 429])

    @mock.patch("api.views.dashboard.render_dashboard_pdf", return_value=b"%PDF")
    def test_spoofed_forwarded_for_is_ignored(self, _render):
        """Only the entry appended by nginx (the last one) identifies the client."""
        url = reverse("dashboard-export-pdf")
        statuses = [
            self.client.post(
                url,
                {"scale": "metropole"},
                format="json",
                HTTP_X_FORWARDED_FOR=f"10.0.0.{i}, 203.0.113.7",
            ).status_code
            for i in range(3)
        ]
        self.assertEqual(statuses, [200, 200, 429])


class ExemptIpTest(ThrottleTestCase):
    @override_settings(THROTTLE_EXEMPT_IPS=["203.0.113.7"])
    def test_exempt_ip_is_never_throttled(self):
        limit = PolygonThrottle().num_requests
        url = reverse("scores-in-polygon", args=["plantability"])
        statuses = self.post_until_throttled(
            url, {}, limit, HTTP_X_FORWARDED_FOR="203.0.113.7"
        )
        self.assertEqual(statuses, [400] * (limit + 1))

    @override_settings(THROTTLE_EXEMPT_IPS=["203.0.113.7"])
    def test_spoofed_exempt_ip_is_still_throttled(self):
        """A client cannot claim the server IP: nginx appends the real one."""
        limit = PolygonThrottle().num_requests
        url = reverse("scores-in-polygon", args=["plantability"])
        statuses = self.post_until_throttled(
            url, {}, limit, HTTP_X_FORWARDED_FOR="203.0.113.7, 198.51.100.1"
        )
        self.assertEqual(statuses, [400] * limit + [429])


class PolygonThrottleTest(ThrottleTestCase):
    def test_scores_in_polygon_is_throttled(self):
        limit = PolygonThrottle().num_requests
        url = reverse("scores-in-polygon", args=["plantability"])
        # An empty body is rejected (400) after the throttle check.
        statuses = self.post_until_throttled(url, {}, limit)
        self.assertEqual(statuses, [400] * limit + [429])

    def test_polygon_endpoints_share_the_limit(self):
        limit = PolygonThrottle().num_requests
        scores_url = reverse("scores-in-polygon", args=["plantability"])
        for _ in range(limit):
            self.client.post(scores_url, {}, format="json")
        response = self.client.post(reverse("dashboard-in-polygon"), {}, format="json")
        self.assertEqual(response.status_code, 429)


class WriteThrottleTest(ThrottleTestCase):
    def test_feedback_is_throttled(self):
        limit = WriteThrottle().num_requests
        # Missing fields are rejected (400) after the throttle check.
        statuses = self.post_until_throttled(reverse("create-feedback"), {}, limit)
        self.assertEqual(statuses, [400] * limit + [429])
