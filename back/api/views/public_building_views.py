import json

from django.contrib.gis.db.models.functions import AsGeoJSON, Transform
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics
from rest_framework.response import Response

from iarbre_data.models import PublicBuilding
from iarbre_data.settings import SRID_DOWNLOADED_DATA

COORDINATES_PRECISION = 6
PROPERTIES = (
    "name",
    "category",
    "nature",
    "nature_detaillee",
    "fictif",
    "student_count",
    "education_priority",
    "capacity",
)


class PublicBuildingListView(generics.ListAPIView):
    def get_queryset(self):
        return PublicBuilding.objects.annotate(
            geojson=AsGeoJSON(
                Transform("geometry", SRID_DOWNLOADED_DATA),
                precision=COORDINATES_PRECISION,
            )
        ).values("id", "geojson", *PROPERTIES)

    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, *args, **kwargs):
        features = [
            {
                "type": "Feature",
                "id": row["id"],
                "geometry": json.loads(row["geojson"]),
                "properties": {key: row[key] for key in PROPERTIES},
            }
            for row in self.get_queryset()
        ]
        return Response({"type": "FeatureCollection", "features": features})
