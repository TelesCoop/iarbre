import os
from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework.views import APIView


class RasterDownloadView(APIView):
    """
    API endpoint to download the plantability raster file.
    Provides a stable URL for accessing the raster regardless of internal file structure.

    Example: GET /api/rasters/plantability/
    """

    def get(self, request):
        """Serve the plantability raster file as a download."""
        raster_path = os.path.join(settings.MEDIA_ROOT, "rasters", "plantability.tif")

        if not os.path.exists(raster_path):
            raise Http404("Plantability raster file not found")

        file_handle = open(raster_path, "rb")

        response = FileResponse(
            file_handle,
            content_type="image/tiff",
            as_attachment=True,
            filename="plantability.tif",
        )

        response["Cache-Control"] = "public, max-age=3600"

        return response
