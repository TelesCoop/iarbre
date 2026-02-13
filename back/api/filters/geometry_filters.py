import logging

from django.contrib.gis.geos import Point
from django_filters import rest_framework as filters

logger = logging.getLogger(__name__)


class PointIntersectsFilter(filters.CharFilter):
    """
    Custom filter that accepts coordinates as comma-separated string "lng,lat"
    and filters geometries that intersect with the point.

    Note: When sent as an array [lng, lat] from the frontend, it will be
    serialized to comma-separated format by URLSearchParams.

    Usage in URL:
        ?geometry__intersects=4.792,45.756
    """

    def filter(self, qs, value):
        if not value:
            return qs

        try:
            # Parse comma-separated values
            coords = value.split(",")
            if len(coords) != 2:
                logger.warning("Expected 2 coordinates, got %d: %s", len(coords), value)
                return qs.none()

            lng, lat = map(float, coords)

            # Create Point geometry (longitude, latitude)
            point = Point(lng, lat, srid=4326)

            # Filter using intersects
            return qs.filter(**{f"{self.field_name}__intersects": point})

        except ValueError:
            logger.warning("Invalid coordinates format: %s", value)
            return qs.none()
