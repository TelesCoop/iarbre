"""Reference data: administrative divisions, boundaries, QPV, public buildings."""

import json

from django.contrib.gis.db.models.functions import AsGeoJSON, Transform
from django.contrib.gis.serializers import geojson
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, mixins, viewsets
from rest_framework.response import Response

from api.constants import ONE_DAY, ONE_MONTH
from api.filters import CityFilterSet, IrisFilterSet
from api.schema import GEOJSON_FEATURE_COLLECTION, TAG_REFERENCE, TAG_MAP_LAYERS
from api.serializers.serializers import CitySerializer, IrisSerializer
from iarbre_data.models import City, Data, Iris, PublicBuilding
from iarbre_data.settings import SRID_DOWNLOADED_DATA

COORDINATES_PRECISION = 6
PUBLIC_BUILDING_PROPERTIES = (
    "name",
    "category",
    "nature",
    "nature_detaillee",
    "student_count",
    "education_priority",
    "capacity",
)


def _geojson_response(queryset, fields) -> Response:
    geojson_string = geojson.Serializer().serialize(
        queryset, geometry_field="geometry", fields=fields
    )
    return Response(json.loads(geojson_string), content_type="application/json")


@extend_schema_view(
    list=extend_schema(
        summary="Liste des communes",
        description=(
            "Communes de la Métropole avec leurs statistiques agrégées (surfaces en "
            "m²). Lyon est découpée en arrondissements (69381 à 69389), le code "
            "69123 ne renvoie rien. `geometry__intersects` attend un point "
            "`lng,lat` en EPSG:4326."
        ),
    ),
    retrieve=extend_schema(summary="Une commune par son identifiant interne"),
)
@extend_schema(tags=[TAG_REFERENCE])
class CityView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet to list and retrieve cities with filtering by code.

    Example: GET /api/cities/?code=69123
    Example: GET /api/cities/?geometry__intersects=4.792,45.756
    """

    queryset = City.objects.all()
    serializer_class = CitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CityFilterSet


@extend_schema_view(
    list=extend_schema(
        summary="Liste des IRIS",
        description=(
            "IRIS (découpage statistique INSEE infra-communal). `city` est l'`id` "
            "interne de la commune. `geometry__intersects` attend un point "
            "`lng,lat` en EPSG:4326."
        ),
    ),
    retrieve=extend_schema(summary="Un IRIS par son identifiant interne"),
)
@extend_schema(tags=[TAG_REFERENCE])
class IrisView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet to list and retrieve IRIS with filtering by code.

    Example: GET /api/iris/?code=691230101
    Example: GET /api/iris/?geometry__intersects=4.792,45.756
    """

    queryset = Iris.objects.all()
    serializer_class = IrisSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IrisFilterSet


@extend_schema(
    tags=[TAG_REFERENCE],
    summary="Contours des communes",
    description="GeoJSON, propriétés `code` et `name`. Cache : 30 jours.",
    responses=GEOJSON_FEATURE_COLLECTION,
)
class CityBoundaryView(generics.ListAPIView):
    def get_queryset(self):
        return City.objects.all()

    @method_decorator(cache_page(ONE_MONTH))
    def get(self, request, *args, **kwargs):
        return _geojson_response(self.get_queryset(), fields=("code", "name"))


@extend_schema(
    tags=[TAG_MAP_LAYERS],
    summary="Quartiers prioritaires de la politique de la ville",
    description="GeoJSON, propriétés `metadata` et `factor`. Cache : 24 heures.",
    responses=GEOJSON_FEATURE_COLLECTION,
)
class QPVListView(generics.ListAPIView):
    def get_queryset(self):
        return Data.objects.filter(factor="QPV")

    @method_decorator(cache_page(ONE_DAY))
    def get(self, request, *args, **kwargs):
        return _geojson_response(
            self.get_queryset(), fields=("id", "metadata", "factor")
        )


@extend_schema(
    tags=[TAG_MAP_LAYERS],
    summary="Bâtiments publics",
    description=(
        "GeoJSON des bâtiments publics (IGN BD TOPO et crèches publiques de Grand "
        "Lyon), coordonnées arrondies à 6 décimales. Propriétés : `name`, "
        "`category`, `nature`, `natureDetaillee`, `studentCount`, "
        "`educationPriority`, `capacity`. Cache : 24 heures."
    ),
    responses=GEOJSON_FEATURE_COLLECTION,
)
class PublicBuildingListView(generics.ListAPIView):
    def get_queryset(self):
        return PublicBuilding.objects.annotate(
            geojson=AsGeoJSON(
                Transform("geometry", SRID_DOWNLOADED_DATA),
                precision=COORDINATES_PRECISION,
            )
        ).values("id", "geojson", *PUBLIC_BUILDING_PROPERTIES)

    @method_decorator(cache_page(ONE_DAY))
    def get(self, request, *args, **kwargs):
        features = [
            {
                "type": "Feature",
                "id": row["id"],
                "geometry": json.loads(row["geojson"]),
                "properties": {key: row[key] for key in PUBLIC_BUILDING_PROPERTIES},
            }
            for row in self.get_queryset()
        ]
        return Response({"type": "FeatureCollection", "features": features})
