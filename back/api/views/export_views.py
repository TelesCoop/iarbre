import logging
import time
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from weasyprint import HTML, default_url_fetcher

logger = logging.getLogger(__name__)
weasyprint_logger = logging.getLogger("weasyprint")

MAX_HTML_SIZE = 10 * 1024 * 1024  # 10 MB


def _no_network_url_fetcher(url, *args, **kwargs):
    if url.startswith("data:"):
        return default_url_fetcher(url, *args, **kwargs)
    raise ValueError(f"Fetching external resources is not allowed: {url}")


class _WarningCounter(logging.Handler):
    """Counts WeasyPrint's own WARNING logs (bad selectors, unknown
    properties, ...) emitted while rendering a single request, so we can
    report a per-export count instead of an undifferentiated log flood."""

    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.count = 0

    def emit(self, record):
        self.count += 1


class DashboardPdfExportView(APIView):
    """Render a fully inlined HTML report (built client-side) to a PDF with WeasyPrint.

    POST /api/dashboard/export-pdf/   body: {"html": "<!doctype html>..."}
    """

    def post(self, request, *args, **kwargs):
        html = request.data.get("html")
        if not html or not isinstance(html, str):
            return Response(
                {"detail": "Missing 'html' field."}, status=status.HTTP_400_BAD_REQUEST
            )
        if len(html) > MAX_HTML_SIZE:
            return Response(
                {"detail": "'html' field is too large."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        debug_path = Path(settings.BASE_DIR) / "last_dashboard_export.html"
        debug_path.write_text(html, encoding="utf-8")
        logger.warning("Dashboard PDF export: raw html dumped to %s", debug_path)

        warning_counter = _WarningCounter()
        weasyprint_logger.addHandler(warning_counter)
        started_at = time.monotonic()
        try:
            pdf_bytes = HTML(
                string=html, url_fetcher=_no_network_url_fetcher
            ).write_pdf()
        except Exception:
            logger.exception(
                "Dashboard PDF export failed: html=%d bytes, %d CSS/rendering warnings "
                "before the failure",
                len(html),
                warning_counter.count,
            )
            raise
        finally:
            weasyprint_logger.removeHandler(warning_counter)
        elapsed = time.monotonic() - started_at

        logger.warning(
            "Dashboard PDF export: html=%d bytes, pdf=%d bytes, %.2fs, %d CSS/rendering warnings",
            len(html),
            len(pdf_bytes),
            elapsed,
            warning_counter.count,
        )

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="rapport-iarbre.pdf"'
        return response
