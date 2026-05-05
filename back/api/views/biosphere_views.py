from django.contrib.gis.geos import Point
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from iarbre_data.models import BiosphereFunctionalIntegrityLandCover
from iarbre_data.settings import SRID_DB, SRID_DOWNLOADED_DATA


class BiosphereLandCoverAtPointView(APIView):
    """Retrieve land use and binary classif for biodiv at a given lat and long."""

    def get(self, request, *args, **kwargs):
        try:
            lat = float(request.query_params["lat"])
            lng = float(request.query_params["lng"])
        except (KeyError, ValueError):
            return Response(
                {
                    "error": "lat and lng query parameters are required and must be numeric"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        point = Point(lng, lat, srid=SRID_DOWNLOADED_DATA)
        point.transform(SRID_DB)

        record = BiosphereFunctionalIntegrityLandCover.objects.filter(
            geometry__intersects=point
        ).first()

        if record is None:
            return Response(
                {"error": "No land cover data found at this location"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "land_cover": record.land_cover,
                "land_cover_label": record.get_land_cover_display(),
                "binary": record.binary,
            }
        )
