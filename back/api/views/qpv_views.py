from rest_framework import generics
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from django.contrib.gis.serializers import geojson
import json

from iarbre_data.models import Data


class QPVListView(generics.ListAPIView):
    def get_queryset(self):
        return Data.objects.filter(factor="QPV")

    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        geojson_string = geojson.Serializer().serialize(
            queryset, geometry_field="geometry", fields=("id", "metadata", "factor")
        )
        geojson_data = json.loads(geojson_string)
        return Response(geojson_data, content_type="application/json")
