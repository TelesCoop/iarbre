from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, Http404
from django.contrib.gis.geos import GEOSGeometry
from django.db.models import Avg, Count, Q
from django.contrib.postgres.aggregates import ArrayAgg

from iarbre_data.models import MVTTile
from iarbre_data.models import Tile, Lcz, Vulnerability
from rest_framework.response import Response

from api.serializers.serializers import (
    LczSerializer,
    VulnerabilitySerializer,
    TileSerializer,
    PlantabilityScoresSerializer,
    VulnerabilityScoresSerializer,
    PlantabilityVulnerabilityScoresSerializer,
)
from api.constants import (
    INDICE_ROUNDING_DECIMALS,
    DataType,
    FrontendDataType,
)

# Mapping of datatypes to their models
DATATYPE_MODEL_MAP = {
    DataType.LCZ.value: Lcz,
    DataType.VULNERABILITY.value: Vulnerability,
    DataType.TILE.value: Tile,
}

# Mapping of frontend datatypes to their models
FRONTEND_DATATYPE_MODEL_MAP = {
    FrontendDataType.VULNERABILITY.value: Vulnerability,
    FrontendDataType.PLANTABILITY.value: Tile,
    FrontendDataType.PLANTABILITY_VULNERABILITY.value: Tile,
}


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
    def _get_serializer_by_datatype(self, datatype):
        serializer_per_datatype = {
            DataType.LCZ.value: LczSerializer,
            DataType.VULNERABILITY.value: VulnerabilitySerializer,
            DataType.TILE.value: TileSerializer,
        }
        if datatype not in serializer_per_datatype:
            raise Http404
        return serializer_per_datatype[datatype]

    def _get_instance_by_datatype(self, instance):
        if instance not in DATATYPE_MODEL_MAP:
            raise Http404
        return DATATYPE_MODEL_MAP[instance]

    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, datatype, id, *args, **kwargs):
        try:
            instance = get_object_or_404(DATATYPE_MODEL_MAP[datatype], id=id)
            serializer = self._get_serializer_by_datatype(datatype)
            return Response(serializer(instance).data)
        except MVTTile.DoesNotExist:
            raise Http404


class ScoresInPolygonView(APIView):
    MAX_POLYGON_AREA_M2 = 10_000_000
    MAX_VERTICES = 10

    def _validate_datatype(self, datatype):
        if datatype not in FRONTEND_DATATYPE_MODEL_MAP:
            return Response(
                {
                    "error": f"Invalid datatype. Must be one of: {', '.join(FRONTEND_DATATYPE_MODEL_MAP.keys())}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if datatype == FrontendDataType.CLIMATE_ZONE.value:
            return Response(
                {
                    "error": "Local climate zone calculation is not supported for polygon selections. Use point selection mode instead."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return None

    def _validate_polygon_data(self, polygon_geojson):
        if not polygon_geojson:
            return Response(
                {"error": "No polygon data provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None

    def _process_polygon_geometry(self, polygon_geojson):
        try:
            polygon = GEOSGeometry(str(polygon_geojson))
            if polygon.srid is None or polygon.srid == 0:
                polygon.srid = 4326
            polygon.transform(2154)

            if polygon.area > self.MAX_POLYGON_AREA_M2:
                return None, Response(
                    {
                        "error": f"Polygon area exceeds maximum allowed size ({self.MAX_POLYGON_AREA_M2 / 1_000_000} km²)"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            num_coords = (
                len(polygon.coords[0])
                if polygon.geom_type == "Polygon"
                else sum(len(ring) for ring in polygon.coords)
            )
            if num_coords > self.MAX_VERTICES:
                return None, Response(
                    {
                        "error": f"Polygon complexity exceeds maximum allowed vertices ({self.MAX_VERTICES})"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return polygon, None

        except Exception as e:
            return None, Response(
                {"error": f"Error processing polygon: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _get_scores_data(self, datatype, tiles):
        if datatype == FrontendDataType.PLANTABILITY.value:
            return (
                self._calculate_plantability_scores(tiles),
                PlantabilityScoresSerializer,
            )

        if datatype == FrontendDataType.VULNERABILITY.value:
            return (
                self._calculate_vulnerability_scores(tiles),
                VulnerabilityScoresSerializer,
            )

        if datatype == FrontendDataType.PLANTABILITY_VULNERABILITY.value:
            return (
                self._calculate_plantability_vulnerability_scores(tiles),
                PlantabilityVulnerabilityScoresSerializer,
            )

        return None, None

    def _get_iris_and_city_codes(self, tiles):
        """Extracts unique IRIS and city codes from a tile queryset"""
        # Single query with conditional aggregation to get distinct codes
        # Note: Only works with Tile model which has iris and city foreign keys
        if tiles.model != Tile:
            # For Lcz and Vulnerability models, return empty lists
            return [], []

        result = tiles.aggregate(
            iris_codes=ArrayAgg(
                "iris__code", distinct=True, filter=Q(iris__code__isnull=False)
            ),
            city_codes=ArrayAgg(
                "city__code", distinct=True, filter=Q(city__code__isnull=False)
            ),
        )

        return (
            [code for code in (result["iris_codes"] or []) if code],
            [code for code in (result["city_codes"] or []) if code],
        )

    def _calculate_plantability_scores(self, tiles):
        """Calculates average scores and distribution for plantability"""

        # Single query to get average and count
        result = tiles.aggregate(
            avg_score=Avg("plantability_normalized_indice"), total_count=Count("id")
        )

        # Single query for distribution using values().annotate()
        distribution_qs = (
            tiles.values("plantability_normalized_indice")
            .annotate(count=Count("id"))
            .order_by("plantability_normalized_indice")
        )

        distribution = {
            str(int(item["plantability_normalized_indice"])): item["count"]
            for item in distribution_qs
            if item["plantability_normalized_indice"] is not None
        }

        avg_score = result["avg_score"]

        return {
            "datatype": DataType.TILE.value,
            "count": result["total_count"],
            "plantability_normalized_indice": (
                round(avg_score, INDICE_ROUNDING_DECIMALS) if avg_score else 0
            ),
            "plantability_indice": (
                round(avg_score, INDICE_ROUNDING_DECIMALS) if avg_score else 0
            ),
            "distribution": distribution,
        }

    def _calculate_vulnerability_scores(self, vulnerabilities):
        """Calculates average scores and distribution for vulnerability"""

        # Single query for averages and count
        result = vulnerabilities.aggregate(
            avg_day=Avg("vulnerability_index_day"),
            avg_night=Avg("vulnerability_index_night"),
            total_count=Count("id"),
        )

        avg_day = result["avg_day"]
        avg_night = result["avg_night"]

        return {
            "datatype": DataType.VULNERABILITY.value,
            "count": result["total_count"],
            "vulnerability_indice_day": (
                round(avg_day, INDICE_ROUNDING_DECIMALS) if avg_day else 0
            ),
            "vulnerability_indice_night": (
                round(avg_night, INDICE_ROUNDING_DECIMALS) if avg_night else 0
            ),
        }

    def _calculate_plantability_vulnerability_scores(self, tiles):
        """Calculates average scores for combined plantability and vulnerability"""

        plantability_data = self._calculate_plantability_scores(tiles)

        vuln_result = (
            tiles.values("vulnerability_idx")
            .distinct()
            .aggregate(
                avg_day=Avg("vulnerability_idx__vulnerability_index_day"),
                avg_night=Avg("vulnerability_idx__vulnerability_index_night"),
            )
        )

        avg_day = vuln_result["avg_day"]
        avg_night = vuln_result["avg_night"]

        return {
            "datatype": FrontendDataType.PLANTABILITY_VULNERABILITY.value,
            "count": plantability_data["count"],
            "plantability_normalized_indice": plantability_data[
                "plantability_normalized_indice"
            ],
            "distribution": plantability_data["distribution"],
            "plantability_indice": plantability_data["plantability_indice"],
            "vulnerability_indice_day": (
                round(avg_day, INDICE_ROUNDING_DECIMALS) if avg_day else 0
            ),
            "vulnerability_indice_night": (
                round(avg_night, INDICE_ROUNDING_DECIMALS) if avg_night else 0
            ),
        }

    def post(self, request, datatype, *args, **kwargs):
        error_response = self._validate_datatype(datatype)
        if error_response:
            return error_response

        polygon_geojson = request.data
        error_response = self._validate_polygon_data(polygon_geojson)
        if error_response:
            return error_response

        polygon, error_response = self._process_polygon_geometry(polygon_geojson)
        if error_response:
            return error_response

        model = FRONTEND_DATATYPE_MODEL_MAP[datatype]
        tiles = model.objects.filter(geometry__intersects=polygon)

        if not tiles.exists():
            return Response(
                {"error": "No tiles found in polygon"},
                status=status.HTTP_404_NOT_FOUND,
            )

        iris_codes, city_codes = self._get_iris_and_city_codes(tiles)
        data, serializer_class = self._get_scores_data(datatype, tiles)

        serializer = serializer_class(
            data={**data, "iris_codes": iris_codes, "city_codes": city_codes}
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
