import json

from django.contrib.gis.serializers import geojson
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics
from rest_framework.response import Response

from iarbre_data.models import City, Iris


class CityBoundaryView(generics.ListAPIView):
    def get_queryset(self):
        return City.objects.all()

    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        geojson_string = geojson.Serializer().serialize(
            queryset, geometry_field="geometry", fields=("code", "name")
        )
        geojson_data = json.loads(geojson_string)
        return Response(geojson_data, content_type="application/json")


class IrisBoundaryView(generics.ListAPIView):
    def get_queryset(self):
        return Iris.objects.all()

    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        geojson_string = geojson.Serializer().serialize(
            queryset, geometry_field="geometry", fields=("code", "name")
        )
        geojson_data = json.loads(geojson_string)
        return Response(geojson_data, content_type="application/json")
