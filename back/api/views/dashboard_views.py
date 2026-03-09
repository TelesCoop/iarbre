from dataclasses import dataclass

from django.contrib.gis.db.models.functions import Area
from django.db.models import Avg, Case, FloatField, QuerySet, Sum, When
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework.views import APIView

from api.constants import INDICE_ROUNDING_DECIMALS
from api.serializers.dashboard_serializer import DashboardSerializer
from iarbre_data.models import City, Iris, Lcz, Vegestrate, Vulnerability

M2_TO_HA = 10_000

BUILT_LCZ_INDICES = {"1", "2", "3", "4", "5", "6", "8", "9"}


def _safe_round(value: float | None) -> float:
    return round(value, INDICE_ROUNDING_DECIMALS) if value is not None else 0


def _m2_to_ha(value: float) -> float:
    return round(value / M2_TO_HA, 1) if value else 0


def _json_avg(key: str) -> Avg:
    """Build Avg(Cast(KeyTextTransform(key, 'details'), FloatField)) expression."""
    return Avg(Cast(KeyTextTransform(key, "details"), output_field=FloatField()))


def _json_avg_built_only(key: str) -> Avg:
    """Avg over built LCZ indices only (conditional aggregation)."""
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
    """Compute weighted average plantability from pre-computed counts dict."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return sum(int(k) * v for k, v in counts.items()) / total


@dataclass
class DashboardScope:
    """Geographic scale resolved from query parameters."""

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
        data = {
            "city": self._serialize_city(scope.city),
            "areaHa": round(scope.area_m2 / M2_TO_HA, 1),
            "plantability": self._aggregate_plantability(scope),
            "vulnerability": self._aggregate_vulnerability(scope.geometry_filter),
            "vegetation": self._aggregate_vegetation(scope),
            "lcz": self._aggregate_lcz(scope.geometry_filter),
        }
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
            }

        total_counts: dict[str, int] = {}
        divisions = []

        for city in scope.cities_qs.only("code", "name", "plantability_counts"):
            for key, count in city.plantability_counts.items():
                total_counts[key] = total_counts.get(key, 0) + count
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

        return {
            "averageNormalizedIndice": _safe_round(_avg_from_counts(total_counts)),
            "distribution": total_counts,
            "distributionByDivision": divisions,
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
            "totalHa": _m2_to_ha(total),
            "treesSurfaceHa": _m2_to_ha(trees),
            "bushesSurfaceHa": _m2_to_ha(bushes),
            "grassSurfaceHa": _m2_to_ha(grass),
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
