from django.contrib.gis.db.models.functions import Area, Intersection
from django.contrib.gis.geos import Point
from django.db.models import F, Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from iarbre_data.models import BiosphereFunctionalIntegrityLandCover
from iarbre_data.utils.biosphere_land_cover import LandCoverClass
from iarbre_data.settings import SRID_DB, SRID_DOWNLOADED_DATA

RADIUS_M = 500


class BiosphereLandCoverAtPointView(APIView):
    """Retrieve distinct land cover types with area percentages within a 500m radius."""

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
        buffer = point.buffer(RADIUS_M)

        records = list(
            BiosphereFunctionalIntegrityLandCover.objects.filter(
                geometry__intersects=buffer
            )
            .values("land_cover", "binary")
            .annotate(total_area=Sum(Area(Intersection("geometry", buffer))))
            .order_by(F("binary").desc(nulls_last=True), "land_cover")
        )

        total = sum(r["total_area"].sq_m for r in records)
        land_cover_labels = dict(LandCoverClass.choices)
        result = [
            {
                "land_cover": r["land_cover"],
                "land_cover_label": land_cover_labels.get(
                    r["land_cover"], r["land_cover"]
                ),
                "binary": r["binary"],
                "percentage": (
                    round(r["total_area"].sq_m / total * 100, 1) if total else 0.0
                ),
            }
            for r in records
        ]
        return Response(result)
