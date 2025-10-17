"""Filters for division models (City, Iris)."""

from django_filters import rest_framework as filters
from iarbre_data.models import City, Iris
from .geometry_filters import PointIntersectsFilter


class CityFilterSet(filters.FilterSet):
    """FilterSet for City with custom geometry intersects filter."""

    geometry__intersects = PointIntersectsFilter(field_name="geometry")

    class Meta:
        model = City
        fields = {
            "code": ["exact", "in"],
        }


class IrisFilterSet(filters.FilterSet):
    """FilterSet for Iris with custom geometry intersects filter."""

    geometry__intersects = PointIntersectsFilter(field_name="geometry")

    class Meta:
        model = Iris
        fields = {
            "code": ["exact", "in"],
        }
