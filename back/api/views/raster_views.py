import os
from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework.views import APIView

RASTER_MAP = {
    "plantability": ("rasters/plantability.tif", "plantability_2025.tif"),
    "vegestrate": (
        "rasters/vegestrate_lyonmetro_02m_postprocessed.tif",
        "vegestrate_2023_02m.tif",
    ),
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
