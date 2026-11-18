"""Spatial queries: feature details, values at a point, aggregates in an area."""

import logging

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.constants import DataType, FrontendDataType
from api.serializers.dashboard_serializer import DashboardSerializer
from api.serializers.serializers import (
    BiosphereFunctionalIntegritySerializer,
    LczSerializer,
    PlantabilityScoresSerializer,
    PlantabilityVulnerabilityScoresSerializer,
    TileSerializer,
    VegestrateSerializer,
    VulnerabilityScoresSerializer,
    VulnerabilitySerializer,
)
from api.services.dashboard import (
    aggregate_plantability,
    aggregate_plantability_from_polygon,
    assemble_dashboard_data,
    division_scope,
    polygon_scope,
)
from api.services.rasters import sample_at_point, vegetation_height_raster
from api.services.spatial import (
    iris_and_city_codes,
    land_cover_at_point,
    polygon_scores,
)
from api.utils.polygon import parse_and_validate_polygon
from iarbre_data.models import (
    BiosphereFunctionalIntegrity,
    City,
    Iris,
    Lcz,
    MVTTile,
    Tile,
    Vegestrate,
    Vulnerability,
)

logger = logging.getLogger(__name__)

# Mapping of datatypes to their models
DATATYPE_MODEL_MAP = {
    DataType.LCZ.value: Lcz,
    DataType.VULNERABILITY.value: Vulnerability,
    DataType.TILE.value: Tile,
    DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY.value: BiosphereFunctionalIntegrity,
    DataType.VEGESTRATE.value: Vegestrate,
}

# Mapping of frontend datatypes to their models
FRONTEND_DATATYPE_MODEL_MAP = {
    FrontendDataType.VULNERABILITY.value: Vulnerability,
    FrontendDataType.PLANTABILITY.value: Tile,
    FrontendDataType.PLANTABILITY_VULNERABILITY.value: Tile,
}

SCORES_SERIALIZER_PER_DATATYPE = {
    FrontendDataType.PLANTABILITY.value: PlantabilityScoresSerializer,
    FrontendDataType.VULNERABILITY.value: VulnerabilityScoresSerializer,
    FrontendDataType.PLANTABILITY_VULNERABILITY.value: PlantabilityVulnerabilityScoresSerializer,
}


def _parse_lat_lng(request) -> tuple[float, float]:
    """Raise KeyError or ValueError when lat/lng are missing or not numeric."""
    return float(request.query_params["lat"]), float(request.query_params["lng"])


# --- Feature details ------------------------------------------------------------


class TileDetailsView(generics.RetrieveAPIView):
    def _get_serializer_by_datatype(self, datatype):
        serializer_per_datatype = {
            DataType.LCZ.value: LczSerializer,
            DataType.VULNERABILITY.value: VulnerabilitySerializer,
            DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY.value: BiosphereFunctionalIntegritySerializer,
            DataType.TILE.value: TileSerializer,
            DataType.VEGESTRATE.value: VegestrateSerializer,
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
            logger.warning(str(serializer))
            return Response(serializer(instance).data)
        except MVTTile.DoesNotExist:
            raise Http404


# --- Values at a point ------------------------------------------------------------


class VegetationHeightAtPointView(APIView):
    def get(self, request):
        try:
            lat, lng = _parse_lat_lng(request)
        except (KeyError, ValueError):
            return Response(
                {"error": "lat and lng required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        raster_path = vegetation_height_raster()
        if not raster_path.exists():
            raise Http404("Vegetation raster not found")

        try:
            return Response({"height": sample_at_point(raster_path, lng, lat)})
        except Exception:
            logger.exception("Error reading vegetation height at %s, %s", lat, lng)
            return Response({"height": None})


class BiosphereLandCoverAtPointView(APIView):
    """Retrieve distinct land cover types with area percentages within a 500m radius."""

    def get(self, request, *args, **kwargs):
        try:
            lat, lng = _parse_lat_lng(request)
        except (KeyError, ValueError):
            return Response(
                {
                    "error": "lat and lng query parameters are required and must be numeric"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(land_cover_at_point(lat, lng))


# --- Aggregates in an area --------------------------------------------------------


class ScoresInPolygonView(APIView):
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

    def post(self, request, datatype, *args, **kwargs):
        error_response = self._validate_datatype(datatype)
        if error_response:
            return error_response

        polygon, error_response = parse_and_validate_polygon(request.data)
        if error_response:
            return error_response

        model = FRONTEND_DATATYPE_MODEL_MAP[datatype]
        tiles = model.objects.filter(geometry__intersects=polygon)

        if not tiles.exists():
            return Response(
                {"error": "No tiles found in polygon"},
                status=status.HTTP_404_NOT_FOUND,
            )

        iris_codes, city_codes = iris_and_city_codes(tiles)
        data = polygon_scores(datatype, tiles)

        serializer = SCORES_SERIALIZER_PER_DATATYPE[datatype](
            data={**data, "iris_codes": iris_codes, "city_codes": city_codes}
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


def _dashboard_response(data: dict) -> Response:
    serializer = DashboardSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.data)


class DashboardView(APIView):
    """Aggregated dashboard data for the metropole, a city, or an IRIS zone.

    GET /api/dashboard/                        -> metropole (all cities)
    GET /api/dashboard/?city_code=69123        -> single city
    GET /api/dashboard/?iris_code=691230101    -> single IRIS
    """

    @method_decorator(cache_page(60 * 60))
    def get(self, request, *args, **kwargs):
        city_code = request.query_params.get("city_code")
        iris_code = request.query_params.get("iris_code")

        city, iris = None, None
        if iris_code:
            iris = get_object_or_404(
                Iris.objects.select_related("city"), code=iris_code
            )
            city = iris.city
        elif city_code:
            city = get_object_or_404(City, code=city_code)

        scope = division_scope(city, iris)
        return _dashboard_response(
            assemble_dashboard_data(scope, aggregate_plantability(scope))
        )


class DashboardPolygonView(APIView):
    """Aggregated dashboard data for a user-drawn polygon.

    POST /api/dashboard/in-polygon/   body: GeoJSON Polygon
    """

    def post(self, request, *args, **kwargs):
        polygon, error_response = parse_and_validate_polygon(request.data)
        if error_response:
            return error_response

        return _dashboard_response(
            assemble_dashboard_data(
                polygon_scope(polygon), aggregate_plantability_from_polygon(polygon)
            )
        )
