import os
from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework.views import APIView

RASTER_MAP = {
    "plantability": ("rasters/plantability.tif", "plantability_2025.tif"),
    "vegestrate": (
        "rasters/vegestrate_lyon_metropole_ir_02.tif",
        "vegestrate_2023_02m.tif",
    ),
}

VECTOR_MAP = {
    "plantability": ("vectors/plantability.fgb", "plantability.fgb"),
    "vegestrate": ("vectors/vegestrate.fgb", "vegestrate.fgb"),
}


class RasterDownloadView(APIView):
    """API endpoint to download the plantability and vegestrate raster files.

    Example: GET /api/rasters/plantability/ or GET /api/rasters/vegestrate/
    """

    def get(self, request, raster_type):
        if raster_type not in RASTER_MAP:
            raise Http404(
                "Raster does not exist, only plantability or vegestrate are available."
            )

        relative_path, filename = RASTER_MAP[raster_type]
        raster_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        if not os.path.exists(raster_path):
            raise Http404(
                "Raster file not found. Please send an email to contact@telescoop.fr"
            )

        response = FileResponse(
            open(raster_path, "rb"),
            content_type="image/tiff",
            as_attachment=True,
            filename=filename,
        )
        response["Cache-Control"] = "public, max-age=3600"
        return response


class VectorDownloadView(APIView):
    """API endpoint to download FlatGeobuf vector files.

    FlatGeobuf includes a spatial index, so QGIS can stream only the
    features within the visible viewport via HTTP range requests.

    Example: GET /api/vectors/plantability/ or GET /api/vectors/vegestrate/
    """

    def get(self, request, vector_type):
        if vector_type not in VECTOR_MAP:
            raise Http404(
                "Vector does not exist, only plantability or vegestrate are available."
            )

        relative_path, filename = VECTOR_MAP[vector_type]
        vector_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        if not os.path.exists(vector_path):
            raise Http404(
                "Vector file not found. Run 'manage.py generate_flatgeobuf' first."
            )

        response = FileResponse(
            open(vector_path, "rb"),
            content_type="application/flatgeobuf",
            as_attachment=True,
            filename=filename,
        )
        response["Cache-Control"] = "public, max-age=3600"
        return response
