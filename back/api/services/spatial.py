"""Spatial queries: scores inside a polygon, land cover around a point."""

from django.contrib.gis.db.models.functions import Area, Intersection
from django.contrib.gis.geos import Point
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Avg, Count, F, Q, QuerySet, Sum

from api.constants import INDICE_ROUNDING_DECIMALS, DataType, FrontendDataType
from iarbre_data.models import BiosphereFunctionalIntegrityLandCover, Tile
from iarbre_data.settings import SRID_DB, SRID_DOWNLOADED_DATA
from iarbre_data.utils.biosphere_land_cover import LandCoverClass

LAND_COVER_RADIUS_M = 500


def _round_or_zero(value: float | None) -> float:
    return round(value, INDICE_ROUNDING_DECIMALS) if value else 0


# --- Scores in polygon --------------------------------------------------------


def polygon_scores(datatype: str, tiles: QuerySet) -> dict:
    """Scores of ``tiles`` (already filtered on the polygon) for a frontend
    datatype among plantability, vulnerability and plantability_vulnerability."""
    if datatype == FrontendDataType.PLANTABILITY.value:
        return _plantability_scores(tiles)
    if datatype == FrontendDataType.VULNERABILITY.value:
        return _vulnerability_scores(tiles)
    if datatype == FrontendDataType.PLANTABILITY_VULNERABILITY.value:
        return _plantability_vulnerability_scores(tiles)
    raise ValueError(f"Unsupported datatype for polygon scores: {datatype}")


def iris_and_city_codes(tiles: QuerySet) -> tuple[list[str], list[str]]:
    """Distinct IRIS and city codes of a tile queryset.

    Only the Tile model has iris and city foreign keys: other models get empty
    lists.
    """
    if tiles.model != Tile:
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


def _plantability_scores(tiles: QuerySet) -> dict:
    result = tiles.aggregate(
        avg_score=Avg("plantability_normalized_indice"), total_count=Count("id")
    )

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

    avg_score = _round_or_zero(result["avg_score"])
    return {
        "datatype": DataType.TILE.value,
        "count": result["total_count"],
        "plantability_normalized_indice": avg_score,
        "plantability_indice": avg_score,
        "distribution": distribution,
    }


def _vulnerability_scores(vulnerabilities: QuerySet) -> dict:
    result = vulnerabilities.aggregate(
        avg_day=Avg("vulnerability_index_day"),
        avg_night=Avg("vulnerability_index_night"),
        total_count=Count("id"),
    )
    return {
        "datatype": DataType.VULNERABILITY.value,
        "count": result["total_count"],
        "vulnerability_indice_day": _round_or_zero(result["avg_day"]),
        "vulnerability_indice_night": _round_or_zero(result["avg_night"]),
    }


def _plantability_vulnerability_scores(tiles: QuerySet) -> dict:
    plantability = _plantability_scores(tiles)

    vuln_result = (
        tiles.values("vulnerability_idx")
        .distinct()
        .aggregate(
            avg_day=Avg("vulnerability_idx__vulnerability_index_day"),
            avg_night=Avg("vulnerability_idx__vulnerability_index_night"),
        )
    )

    return {
        "datatype": FrontendDataType.PLANTABILITY_VULNERABILITY.value,
        "count": plantability["count"],
        "plantability_normalized_indice": plantability[
            "plantability_normalized_indice"
        ],
        "distribution": plantability["distribution"],
        "plantability_indice": plantability["plantability_indice"],
        "vulnerability_indice_day": _round_or_zero(vuln_result["avg_day"]),
        "vulnerability_indice_night": _round_or_zero(vuln_result["avg_night"]),
    }


# --- Land cover around a point ------------------------------------------------


def land_cover_at_point(lat: float, lng: float) -> list[dict]:
    """Distinct land cover types with their area share within
    ``LAND_COVER_RADIUS_M`` of a WGS84 point."""
    point = Point(lng, lat, srid=SRID_DOWNLOADED_DATA)
    point.transform(SRID_DB)
    buffer = point.buffer(LAND_COVER_RADIUS_M)

    records = list(
        BiosphereFunctionalIntegrityLandCover.objects.filter(
            geometry__intersects=buffer
        )
        .values("land_cover", "binary")
        .annotate(total_area=Sum(Area(Intersection("geometry", buffer))))
        .order_by(F("binary").desc(nulls_last=True), "land_cover")
    )

    total = sum(r["total_area"].sq_m for r in records)
    land_cover_labels = dict(LandCoverClass.choices)
    return [
        {
            "land_cover": r["land_cover"],
            "land_cover_label": land_cover_labels.get(r["land_cover"], r["land_cover"]),
            "binary": r["binary"],
            "percentage": (
                round(r["total_area"].sq_m / total * 100, 1) if total else 0.0
            ),
        }
        for r in records
    ]
