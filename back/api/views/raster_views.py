from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.views import APIView

from api.management.commands.export_vectors import get_vector_file_map

RASTER_MAP = {
    "plantability": ("rasters/plantability.tif", "plantability_2025.tif"),
    "vegestrate": (
        "rasters/vegestrate_lyon_metropole_ir_02.tif",
        "vegestrate_2023_02m.tif",
    ),
}

CONTENT_TYPES = {
    "flatgeobuf": "application/flatgeobuf",
    "geoparquet": "application/x-parquet",
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
    """Download plantability/vegestrate raster files (GeoTIFF).

    Example: GET /api/rasters/plantability/
    """

    file_map = RASTER_MAP
    download_content_type = "image/tiff"

    def get(self, request, raster_type: str):
        return super().get(request, raster_type)


class VectorDownloadView(APIView):
    """Download plantability/vegestrate vector files.

    Supports FlatGeobuf (default) and GeoParquet via the ``format`` query
    parameter.

    Examples:
        GET /api/vectors/plantability/                  -> FlatGeobuf
        GET /api/vectors/plantability/?format=geoparquet -> GeoParquet
    """

    EXT_TO_FORMAT = {"fgb": "flatgeobuf", "parquet": "geoparquet"}

    def get(self, request, vector_type: str, ext: str = None):
        if ext:
            fmt = self.EXT_TO_FORMAT.get(ext)
            if not fmt:
                raise Http404(f"Unknown extension '.{ext}'.")
        else:
            fmt = request.query_params.get("format", "flatgeobuf")
        if fmt not in CONTENT_TYPES:
            available = ", ".join(CONTENT_TYPES)
            raise Http404(f"Unknown format '{fmt}'. Available: {available}.")

        file_map = get_vector_file_map(fmt)
        if vector_type not in file_map:
            available = ", ".join(file_map)
            raise Http404(f"Unknown dataset '{vector_type}'. Available: {available}.")

        relative_path, filename = file_map[vector_type]
        full_path = Path(settings.MEDIA_ROOT) / relative_path

        if not full_path.exists():
            raise Http404(
                f"File not found: {filename}. Run 'manage.py export_vectors' first."
            )

        response = FileResponse(
            full_path.open("rb"),
            content_type=CONTENT_TYPES[fmt],
            filename=filename,
        )
        response["Cache-Control"] = "public, max-age=3600"
        return response
