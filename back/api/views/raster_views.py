import os
from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework.views import APIView

from api.constants import VEGESTRATE_FILES


class RasterDownloadView(APIView):
    """API endpoint to download plantability and vegestrate raster files.

    For plantability:
        GET /api/rasters/plantability/

    For vegestrate, query parameters control which file is served:
        GET /api/rasters/vegestrate/?year=2023&resolution=02&postprocess=true&version=3

    Supported vegestrate combinations:
        year=2018, postprocess=false                 -> raw 2018
        year=2018, postprocess=true, version=3       -> post-processed v3 2018
        year=2023, postprocess=false                 -> raw 2023
        year=2023, postprocess=true, version=1       -> post-processed v1 2023
        year=2023, postprocess=true, version=2       -> post-processed v2 2023
        year=2023, postprocess=true, version=3       -> post-processed v3 2023
    """

    def get(self, request, raster_type):
        if raster_type == "plantability":
            relative_path = "rasters/plantability.tif"
            filename = "plantability_2025.tif"
        elif raster_type == "vegestrate":
            year = int(request.query_params.get("year", 2023))
            resolution = request.query_params.get("resolution", "02")
            postprocess = (
                request.query_params.get("postprocess", "true").lower() == "true"
            )
            version_param = request.query_params.get("version", "")
            version = int(version_param) if version_param and postprocess else None

            filename_tif = VEGESTRATE_FILES.get(
                (year, resolution, postprocess, version)
            )
            if not filename_tif:
                raise Http404("No raster file for the requested parameters")

            relative_path = os.path.join("rasters/vegestrate", filename_tif)
            filename = filename_tif
        else:
            raise Http404(
                "Raster does not exist, only plantability or vegestrate are available."
            )

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
