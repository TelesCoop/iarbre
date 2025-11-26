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

# Mapping des datatypes vers leurs modèles
DATATYPE_MODEL_MAP = {
    DataType.LCZ.value: Lcz,
    DataType.VULNERABILITY.value: Vulnerability,
    DataType.TILE.value: Tile,
}

# Mapping des datatypes frontend vers leurs modèles
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
    """
    API endpoint pour récupérer les scores moyens et la distribution des tuiles dans un polygone
    """

    def _get_iris_and_city_codes(self, tiles):
        """Extrait les codes IRIS et communes uniques depuis un queryset de tuiles"""
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
        """Calcule les scores moyens et la distribution pour la plantabilité"""

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
        """Calcule les scores moyens et la distribution pour la vulnérabilité"""

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
        """Calcule les scores moyens pour plantabilité et vulnérabilité combinés"""

        # Calculate plantability scores from tiles
        plantability_data = self._calculate_plantability_scores(tiles)

        # Get unique vulnerability objects from tiles
        vulnerabilities = Vulnerability.objects.filter(
            id__in=tiles.values_list("vulnerability_idx", flat=True).distinct()
        )

        # Calculate vulnerability scores from vulnerability objects
        vulnerability_data = self._calculate_vulnerability_scores(vulnerabilities)

        # Fusionner les résultats en excluant les champs redondants
        return {
            "datatype": FrontendDataType.PLANTABILITY_VULNERABILITY.value,
            "count": plantability_data["count"],
            "plantability_normalized_indice": plantability_data[
                "plantability_normalized_indice"
            ],
            "plantability_indice": plantability_data["plantability_indice"],
            "vulnerability_indice_day": vulnerability_data["vulnerability_indice_day"],
            "vulnerability_indice_night": vulnerability_data[
                "vulnerability_indice_night"
            ],
        }

    def post(self, request, datatype, *args, **kwargs):
        """
        Accepte un GeoJSON polygon et retourne les scores moyens et la distribution

        Request body:
        {
            "type": "Polygon",
            "coordinates": [[[lng, lat], [lng, lat], ...]]
        }

        Response (plantability):
        {
            "datatype": "plantability",
            "count": 150,
            "plantabilityNormalizedIndice": 6.5,
            "plantabilityIndice": 6.5,
            "distribution": {
                "0": 5,
                "1": 10,
                "2": 15,
                ...
            }
        }

        Response (vulnerability):
        {
            "datatype": "vulnerability",
            "count": 150,
            "vulnerability_indice_day": 4.2,
            "vulnerability_indice_night": 3.8,
        }
        """
        if datatype not in FRONTEND_DATATYPE_MODEL_MAP:
            return Response(
                {
                    "error": f"Invalid datatype. Must be one of: {', '.join(FRONTEND_DATATYPE_MODEL_MAP.keys())}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Vérifier que le datatype n'est pas LCZ (zones climatiques locales)
        if datatype == FrontendDataType.CLIMATE_ZONE.value:
            return Response(
                {
                    "error": "Le calcul des zones climatiques locales n'est pas supporté pour les sélections de type polygone. Utilisez le mode de sélection par point."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        polygon_geojson = request.data
        if not polygon_geojson:
            return Response(
                {"error": "No polygon data provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Convertir le GeoJSON en geometry PostGIS
            polygon = GEOSGeometry(str(polygon_geojson))
            if polygon.srid is None or polygon.srid == 0:
                polygon.srid = 4326
            polygon.transform(2154)

            # Récupérer le modèle approprié
            model = FRONTEND_DATATYPE_MODEL_MAP[datatype]

            # Requête PostGIS pour trouver les tuiles qui intersectent le polygone
            tiles = model.objects.filter(geometry__intersects=polygon)

            if not tiles.exists():
                return Response(
                    {"error": "No tiles found in polygon"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Extraire les codes IRIS et communes
            iris_codes, city_codes = self._get_iris_and_city_codes(tiles)

            # Calculer les scores et distributions selon le datatype
            if datatype == FrontendDataType.PLANTABILITY.value:
                data = self._calculate_plantability_scores(tiles)
                serializer_class = PlantabilityScoresSerializer

            elif datatype == FrontendDataType.VULNERABILITY.value:
                data = self._calculate_vulnerability_scores(tiles)
                serializer_class = VulnerabilityScoresSerializer

            elif datatype == FrontendDataType.PLANTABILITY_VULNERABILITY.value:
                data = self._calculate_plantability_vulnerability_scores(tiles)
                serializer_class = PlantabilityVulnerabilityScoresSerializer

            # Fusionner les données avec les codes
            serializer = serializer_class(
                data={**data, "iris_codes": iris_codes, "city_codes": city_codes}
            )
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": f"Error processing polygon: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
