from django.shortcuts import get_object_or_404
from rest_framework import generics
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, Http404
from iarbre_data.models import MVTTile
from iarbre_data.models import Tile, Lcz, Vulnerability
from rest_framework.response import Response

from api.serializers.serializers import (
    LczSerializer,
    VulnerabilitySerializer,
    TileSerializer,
)


class TileView(generics.RetrieveAPIView):
    def get_object(self):
        return MVTTile.objects.get(
            geolevel=self.kwargs.get("geolevel"),
            datatype=self.kwargs.get("datatype"),
            zoom_level=self.kwargs.get("zoom"),
            tile_x=self.kwargs.get("x"),
            tile_y=self.kwargs.get("y"),
        )

    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, *args, **kwargs):
        try:
            return HttpResponse(
                self.get_object().mvt_file, content_type="application/x-protobuf"
            )
        except MVTTile.DoesNotExist:
            raise Http404


class TileDetailsView(generics.RetrieveAPIView):
    instance_per_datatype = {
        "lcz": Lcz,
        "vulnerability": Vulnerability,
        "plantability": Tile,
    }

    def _get_serializer_by_datatype(self, datatype):
        serializer_per_datatype = {
            "lcz": LczSerializer,
            "vulnerability": VulnerabilitySerializer,
            "plantability": TileSerializer,
        }
        if datatype not in serializer_per_datatype:
            raise Http404
        return serializer_per_datatype[datatype]

    def _get_instance_by_datatype(self, instance):
        instance_per_datatype = {
            "lcz": Lcz,
            "vulnerability": Vulnerability,
            "plantability": Tile,
        }
        if instance not in instance_per_datatype:
            raise Http404
        return instance_per_datatype[instance]

    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, datatype, id, *args, **kwargs):
        try:
            instance = get_object_or_404(self.instance_per_datatype[datatype], id=id)
            serializer = self._get_serializer_by_datatype(datatype)
            return Response(serializer(instance).data)
        except MVTTile.DoesNotExist:
            raise Http404
