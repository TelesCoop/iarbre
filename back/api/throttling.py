"""Rate limits for the costly or abusable endpoints.

Each throttle has its own scope; rates live in
``REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]``. Clients are identified by IP,
authenticated or not (``NUM_PROXIES`` tells DRF which X-Forwarded-For entry to
trust). Counters are kept in the ``throttle`` cache, shared between workers.
"""

from django.core.cache import caches
from rest_framework.throttling import SimpleRateThrottle


class _IpThrottle(SimpleRateThrottle):
    @property
    def cache(self):
        # Resolved on each use, so tests overriding CACHES are honored.
        return caches["throttle"]

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }


class WriteThrottle(_IpThrottle):
    """User writes: feedback (sends an email) and short links."""

    scope = "writes"


class PolygonThrottle(_IpThrottle):
    """Spatial aggregates over a user-drawn polygon."""

    scope = "polygon"


class PdfExportBurstThrottle(_IpThrottle):
    """PDF export renders the dashboard in a headless browser."""

    scope = "pdf_export_burst"


class PdfExportSustainedThrottle(_IpThrottle):
    scope = "pdf_export_sustained"
