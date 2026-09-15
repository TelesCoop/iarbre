from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.views import APIView

from api.constants import VEGESTRATE_FILES


def _entry(path: str, filename: str | None = None) -> tuple[str, str]:
    """Build a ``(path, filename)`` tuple, defaulting filename to basename."""
    return path, filename or Path(path).name


base_dir = "rasters/WMS/"
RASTER_MAP: dict[str, tuple[str, str]] = {
    "plantability": _entry(base_dir + "plantability.tif"),
    "plantability_colors": _entry(base_dir + "plantability_2025.tif"),
    "vegestrate": _entry(base_dir + "vegestrate_02_2023.tif"),
    "vegestrate_ndsm": _entry(base_dir + "vegestrate_02_2023_elevation.tif"),
    "vulnerability": _entry(base_dir + "vulnerability.tif"),
    "vulnerability_colors": _entry(base_dir + "vulnerability_colors.tif"),
    "lcz": _entry(base_dir + "lcz.tif"),
    "lcz_colors": _entry(base_dir + "lcz_colors.tif"),
}


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
    """Download raster files (GeoTIFF). Example: ``GET /api/rasters/plantability/``.

    For ``raster_type=vegestrate`` with a ``year`` query parameter, serves a
    specific archived export instead of the default file:

        GET /api/rasters/vegestrate/?year=2023&resolution=02&postprocess=true&version=3
    """

    file_map = RASTER_MAP
    download_content_type = "image/tiff"

    def get(self, request, raster_type: str):
        if raster_type == "vegestrate" and "year" in request.query_params:
            return self._get_vegestrate_archive(request)
        return super().get(request, raster_type)

    def _get_vegestrate_archive(self, request):
        year = int(request.query_params.get("year", 2023))
        resolution = request.query_params.get("resolution", "02")
        postprocess = request.query_params.get("postprocess", "true").lower() == "true"
        version_param = request.query_params.get("version", "")
        version = int(version_param) if version_param and postprocess else None
        kind = request.query_params.get("kind", "class")

        filename = VEGESTRATE_FILES.get((year, resolution, postprocess, version, kind))
        if not filename:
            raise Http404("No raster file for the requested parameters")

        full_path = Path(settings.MEDIA_ROOT) / "rasters/vegestrate" / filename
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
