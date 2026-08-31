from dataclasses import dataclass

from django.contrib.gis.db.models.functions import Area
from django.db.models import Avg, Case, Count, FloatField, QuerySet, Sum, When
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.utils.pdf_export import get_export_scope

from api.constants import INDICE_ROUNDING_DECIMALS
from api.serializers.dashboard_serializer import DashboardSerializer
from api.utils.polygon import parse_and_validate_polygon
from iarbre_data.models import (
    BiosphereFunctionalIntegrity,
    City,
    Data,
    Iris,
    Lcz,
    Tile,
    Vegestrate,
    Vulnerability,
)

M2_TO_KM2 = 1_000_000

BUILT_LCZ_INDICES = {"1", "2", "3", "4", "5", "6", "8", "9"}


def _safe_round(value: float | None) -> float:
    return round(value, INDICE_ROUNDING_DECIMALS) if value is not None else 0


def _json_avg(key: str) -> Avg:
    return Avg(Cast(KeyTextTransform(key, "details"), output_field=FloatField()))


def _json_avg_built_only(key: str) -> Avg:
    return Avg(
        Case(
            When(
                lcz_index__in=BUILT_LCZ_INDICES,
                then=Cast(KeyTextTransform(key, "details"), output_field=FloatField()),
            ),
            output_field=FloatField(),
        )
    )


def _avg_from_counts(counts: dict) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return sum(int(k) * v for k, v in counts.items()) / total


@dataclass
class DashboardScope:
    city: City | None
    iris: Iris | None
    geometry_filter: dict
    cities_qs: QuerySet[City]
    area_m2: float


class DashboardView(APIView):
    """Aggregated dashboard data for the metropole, a city, or an IRIS zone.

    GET /api/dashboard/                        -> metropole (all cities)
    GET /api/dashboard/?city_code=69123        -> single city
    GET /api/dashboard/?iris_code=691230101    -> single IRIS
    """

    @method_decorator(cache_page(60 * 60))
    def get(self, request, *args, **kwargs):
        scope = self._get_geographic_scale(request)
        data = assemble_dashboard_data(scope, self._aggregate_plantability(scope))
        serializer = DashboardSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @staticmethod
    def _get_geographic_scale(request) -> DashboardScope:
        city_code = request.query_params.get("city_code")
        iris_code = request.query_params.get("iris_code")
        cities_qs = City.objects.all()

        city, iris, geometry = None, None, None

        if iris_code:
            iris = get_object_or_404(
                Iris.objects.select_related("city"), code=iris_code
            )
            city = iris.city
            geometry = iris.geometry
        elif city_code:
            city = get_object_or_404(City, code=city_code)
            geometry = city.geometry

        if geometry:
            area_m2 = geometry.area
        else:
            area_m2 = (
                cities_qs.annotate(geom_area=Area("geometry"))
                .aggregate(total=Sum("geom_area"))["total"]
                .sq_m
            )

        return DashboardScope(
            city=city,
            iris=iris,
            geometry_filter={"geometry__intersects": geometry} if geometry else {},
            cities_qs=cities_qs,
            area_m2=area_m2,
        )

    @staticmethod
    def _serialize_city(city: City | None) -> dict | None:
        if not city:
            return None
        return {"id": city.id, "code": city.code, "name": city.name}

    @staticmethod
    def _plantability_by_subdivision(divisions: QuerySet) -> list[dict]:
        return [
            {
                "code": d.code,
                "name": d.name or d.code,
                "averageNormalizedIndice": _safe_round(
                    _avg_from_counts(d.plantability_counts)
                ),
                "distribution": d.plantability_counts,
            }
            for d in divisions.only("code", "name", "plantability_counts")
        ]

    def _aggregate_plantability(self, scope: DashboardScope) -> dict:
        if scope.iris:
            return {
                "averageNormalizedIndice": _safe_round(
                    _avg_from_counts(scope.iris.plantability_counts)
                ),
                "distribution": scope.iris.plantability_counts,
                "distributionByDivision": [],
                "metaFactors": scope.iris.meta_factors_avg or {},
            }

        if scope.city:
            return {
                "averageNormalizedIndice": _safe_round(
                    _avg_from_counts(scope.city.plantability_counts)
                ),
                "distribution": scope.city.plantability_counts,
                "distributionByDivision": self._plantability_by_subdivision(
                    Iris.objects.filter(city=scope.city)
                ),
                "metaFactors": scope.city.meta_factors_avg or {},
            }

        total_counts: dict[str, int] = {}
        meta_totals: dict[str, float] = {}
        meta_city_count = 0
        divisions = []

        for city in scope.cities_qs.only(
            "code", "name", "plantability_counts", "meta_factors_avg"
        ):
            for key, count in city.plantability_counts.items():
                total_counts[key] = total_counts.get(key, 0) + count
            if city.meta_factors_avg:
                for key, val in city.meta_factors_avg.items():
                    meta_totals[key] = meta_totals.get(key, 0.0) + val
                meta_city_count += 1
            divisions.append(
                {
                    "code": city.code,
                    "name": city.name or city.code,
                    "averageNormalizedIndice": _safe_round(
                        _avg_from_counts(city.plantability_counts)
                    ),
                    "distribution": city.plantability_counts,
                }
            )

        meta_factors_avg = (
            {k: _safe_round(v / meta_city_count) for k, v in meta_totals.items()}
            if meta_city_count > 0
            else {}
        )

        return {
            "averageNormalizedIndice": _safe_round(_avg_from_counts(total_counts)),
            "distribution": total_counts,
            "distributionByDivision": divisions,
            "metaFactors": meta_factors_avg,
        }

    @staticmethod
    def _aggregate_vulnerability(geometry_filter: dict) -> dict:
        qs = Vulnerability.objects.all()
        if geometry_filter:
            qs = qs.filter(**geometry_filter)

        result = qs.aggregate(
            avg_day=Avg("vulnerability_index_day"),
            avg_night=Avg("vulnerability_index_night"),
            avg_expo_day=Avg("expo_index_day"),
            avg_expo_night=Avg("expo_index_night"),
            avg_sensibility_day=Avg("sensibilty_index_day"),
            avg_sensibility_night=Avg("sensibilty_index_night"),
            avg_capaf_day=Avg("capaf_index_day"),
            avg_capaf_night=Avg("capaf_index_night"),
        )

        return {
            "averageDay": _safe_round(result["avg_day"]),
            "averageNight": _safe_round(result["avg_night"]),
            "expoDay": _safe_round(result["avg_expo_day"]),
            "expoNight": _safe_round(result["avg_expo_night"]),
            "sensibilityDay": _safe_round(result["avg_sensibility_day"]),
            "sensibilityNight": _safe_round(result["avg_sensibility_night"]),
            "capafDay": _safe_round(result["avg_capaf_day"]),
            "capafNight": _safe_round(result["avg_capaf_night"]),
        }

    @staticmethod
    def _aggregate_vegetation(scope: DashboardScope) -> dict:
        qs = Vegestrate.objects.all()
        if scope.geometry_filter:
            qs = qs.filter(**scope.geometry_filter)

        by_strate = {
            row["strate"]: row["total"]
            for row in qs.values("strate").annotate(total=Sum("surface"))
        }

        trees = by_strate.get("arborescent", 0) or 0
        bushes = by_strate.get("arbustif", 0) or 0
        grass = by_strate.get("herbacee", 0) or 0
        total = trees + bushes + grass

        return {
            "totalM2": total,
            "treesSurfaceM2": trees,
            "bushesSurfaceM2": bushes,
            "grassSurfaceM2": grass,
        }

    @staticmethod
    def _aggregate_lcz(geometry_filter: dict) -> dict:
        qs = Lcz.objects.all()
        if geometry_filter:
            qs = qs.filter(**geometry_filter)

        result = qs.aggregate(
            avg_hre_built=_json_avg_built_only("hre"),
            avg_bur_built=_json_avg_built_only("bur"),
            avg_ror=_json_avg("ror"),
            avg_bsr=_json_avg("bsr"),
            avg_bur=_json_avg("bur"),
            avg_war=_json_avg("war"),
            avg_ver=_json_avg("ver"),
            avg_vhr=_json_avg("vhr"),
        )

        return {
            "averageBuildingSurfaceRate": _safe_round(result["avg_bur_built"]),
            "averageBuildingHeight": _safe_round(result["avg_hre_built"]),
            "impermeableSurfaceRate": _safe_round(result["avg_ror"]),
            "permeableSoilRate": _safe_round(result["avg_bsr"]),
            "buildingRate": _safe_round(result["avg_bur"]),
            "treeCoverRate": _safe_round(result["avg_vhr"]),
            "totalVegetationRate": _safe_round(result["avg_ver"]),
            "waterRate": _safe_round(result["avg_war"]),
        }

    @staticmethod
    def _aggregate_buildings(geometry_filter: dict) -> dict:
        qs = Data.objects.filter(factor="Bâtiments")
        if geometry_filter:
            qs = qs.filter(**geometry_filter)
        result = qs.annotate(
            area_m2=Cast(Area("geometry"), output_field=FloatField())
        ).aggregate(avg_area=Avg("area_m2"))
        avg = result["avg_area"]
        return {"averageBuildingFootprintM2": _safe_round(avg)}

    @staticmethod
    def _aggregate_biosphere(geometry_filter: dict) -> dict:
        qs = BiosphereFunctionalIntegrity.objects.all()
        if geometry_filter:
            qs = qs.filter(**geometry_filter)
        distribution = {
            str(row["indice"]): row["count"]
            for row in qs.values("indice")
            .annotate(count=Count("id"))
            .order_by("indice")
        }
        return {
            "averageIndice": _safe_round(_avg_from_counts(distribution)),
            "distribution": distribution,
        }


def assemble_dashboard_data(scope: DashboardScope, plantability: dict) -> dict:
    """Build the dashboard payload from a scope and a precomputed plantability dict.

    Shared by the predefined-scale view (GET) and the drawn-polygon view (POST):
    every aggregation but plantability already works off ``scope.geometry_filter``.
    """
    return {
        "city": DashboardView._serialize_city(scope.city),
        "areaKm2": round(scope.area_m2 / M2_TO_KM2, 3),
        "plantability": plantability,
        "vulnerability": DashboardView._aggregate_vulnerability(scope.geometry_filter),
        "vegetation": DashboardView._aggregate_vegetation(scope),
        "lcz": DashboardView._aggregate_lcz(scope.geometry_filter),
        "buildings": DashboardView._aggregate_buildings(scope.geometry_filter),
        "biosphere": DashboardView._aggregate_biosphere(scope.geometry_filter),
    }


def _meta_factors_from_iris_counts(counts_by_iris: dict[int, int]) -> dict:
    """Tile-count-weighted average of the meta_factors_avg of intersected IRIS."""
    if not counts_by_iris:
        return {}

    weighted: dict[str, float] = {}
    total_weight = 0
    for iris in Iris.objects.filter(id__in=counts_by_iris.keys()).only(
        "id", "meta_factors_avg"
    ):
        if not iris.meta_factors_avg:
            continue
        weight = counts_by_iris[iris.id]
        total_weight += weight
        for key, value in iris.meta_factors_avg.items():
            weighted[key] = weighted.get(key, 0.0) + value * weight

    if total_weight == 0:
        return {}
    return {key: _safe_round(value / total_weight) for key, value in weighted.items()}


def _aggregate_plantability_from_polygon(polygon) -> dict:
    """Plantability for an arbitrary polygon, computed from intersected tiles
    (no precomputed plantability_counts exist for a drawn zone)."""
    tile_rows = Tile.objects.filter(geometry__intersects=polygon).values(
        "plantability_normalized_indice", "iris"
    )

    distribution: dict[str, int] = {}
    counts_by_iris: dict[int, int] = {}
    for row in tile_rows:
        indice = row["plantability_normalized_indice"]
        if indice is not None:
            key = str(int(indice))
            distribution[key] = distribution.get(key, 0) + 1
        iris_id = row["iris"]
        if iris_id is not None:
            counts_by_iris[iris_id] = counts_by_iris.get(iris_id, 0) + 1

    return {
        "averageNormalizedIndice": _safe_round(_avg_from_counts(distribution)),
        "distribution": distribution,
        "distributionByDivision": [],
        "metaFactors": _meta_factors_from_iris_counts(counts_by_iris),
    }


class DashboardPolygonView(APIView):
    """Aggregated dashboard data for a user-drawn polygon.

    POST /api/dashboard/in-polygon/   body: GeoJSON Polygon
    """

    def post(self, request, *args, **kwargs):
        polygon, error_response = parse_and_validate_polygon(request.data)
        if error_response:
            return error_response

        scope = DashboardScope(
            city=None,
            iris=None,
            geometry_filter={"geometry__intersects": polygon},
            cities_qs=City.objects.none(),
            area_m2=polygon.area,
        )
        data = assemble_dashboard_data(
            scope, _aggregate_plantability_from_polygon(polygon)
        )
        serializer = DashboardSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class DashboardExportScopeView(APIView):
    def get(self, request, token, *args, **kwargs):
        scope = get_export_scope(token)
        if scope is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(scope)
