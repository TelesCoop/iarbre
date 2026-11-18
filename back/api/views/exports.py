"""Downloads: raster files and dashboard PDF reports."""

from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.constants import PET_RASTERS, SHADOW_RASTER
from api.utils.pdf_export import get_export_scope, store_export_scope
from api.utils.pdf_renderer import PdfExportTimeout, render_dashboard_pdf


def _entry(path: str, filename: str | None = None) -> tuple[str, str]:
    """Build a ``(path, filename)`` tuple, defaulting filename to basename."""
    return path, filename or Path(path).name


base_dir = "rasters/WMS/"
RASTER_MAP: dict[str, tuple[str, str]] = {
    "plantability": _entry(base_dir + "plantability.tif"),
    "plantability_colors": _entry("rasters/plantability_colors.tif"),
    "vegestrate": _entry(base_dir + "vegestrate_02_2023.tif"),
    "vegestrate_ndsm": _entry(base_dir + "vegestrate_02_2023_elevation.tif"),
    "vulnerability": _entry(base_dir + "vulnerability.tif"),
    "vulnerability_colors": _entry(base_dir + "vulnerability_colors.tif"),
    "lcz": _entry(base_dir + "lcz.tif"),
    "lcz_colors": _entry(base_dir + "lcz_colors.tif"),
    **{
        f"pet_{year}": _entry(f"{base_dir}{name}.tif")
        for year, name in PET_RASTERS.items()
    },
    "shadow": _entry(f"{base_dir}{SHADOW_RASTER}.tif"),
}


# --- Raster files -------------------------------------------------------------------


class FileDownloadView(APIView):
    """Base view for serving pre-generated static files from MEDIA_ROOT.

    Subclasses set ``file_map`` and ``download_content_type`` to configure
    which files are available and how they are served.
    """

    file_map: dict[str, tuple[str, str]] = {}
    download_content_type: str = "application/octet-stream"

    def get(self, request, file_key: str):
        if file_key not in self.file_map:
            available = ", ".join(self.file_map)
            raise Http404(f"Unknown key '{file_key}'. Available: {available}.")

        relative_path, filename = self.file_map[file_key]
        full_path = Path(settings.MEDIA_ROOT) / relative_path

        if not full_path.exists():
            raise Http404(f"File not found: {filename}.")

        response = FileResponse(
            full_path.open("rb"),
            content_type=self.download_content_type,
            as_attachment=True,
            filename=filename,
        )
        response["Cache-Control"] = "public, max-age=3600"
        return response


class RasterDownloadView(FileDownloadView):
    """Download raster files (GeoTIFF). Example: ``GET /api/rasters/plantability/``."""

    file_map = RASTER_MAP
    download_content_type = "image/tiff"

    def get(self, request, raster_type: str):
        return super().get(request, raster_type)


# --- Dashboard PDF ------------------------------------------------------------------


class DashboardExportScopeView(APIView):
    """Scope of a pending PDF export, read back by the headless browser."""

    def get(self, request, token, *args, **kwargs):
        scope = get_export_scope(token)
        if scope is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(scope)


class DashboardExportPdfView(APIView):
    def post(self, request, *args, **kwargs):
        token = store_export_scope(request.data)
        frontend_url = settings.PDF_EXPORT_FRONTEND_URL or request.build_absolute_uri(
            "/"
        ).rstrip("/")
        try:
            pdf_bytes = render_dashboard_pdf(token, frontend_url)
        except PdfExportTimeout:
            return Response(
                {"detail": "PDF generation timed out"},
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="rapport.pdf"'
        return response
