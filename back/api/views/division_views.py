from rest_framework import mixins, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from iarbre_data.models import City, Iris
from api.serializers.serializers import CitySerializer, IrisSerializer
from api.filters import CityFilterSet, IrisFilterSet


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
