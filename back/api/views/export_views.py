from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from weasyprint import HTML, default_url_fetcher

MAX_HTML_SIZE = 10 * 1024 * 1024  # 10 MB


def _no_network_url_fetcher(url, *args, **kwargs):
    if url.startswith("data:"):
        return default_url_fetcher(url, *args, **kwargs)
    raise ValueError(f"Fetching external resources is not allowed: {url}")


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

        pdf_bytes = HTML(string=html, url_fetcher=_no_network_url_fetcher).write_pdf()

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="rapport-iarbre.pdf"'
        return response
