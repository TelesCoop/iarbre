import logging

from django.contrib.gis.geos import GEOSGeometry
from rest_framework import status
from rest_framework.response import Response

from iarbre_data.settings import SRID_DB, SRID_DOWNLOADED_DATA

logger = logging.getLogger(__name__)

MAX_POLYGON_AREA_M2 = 10_000_000
MAX_VERTICES = 10


def parse_and_validate_polygon(polygon_geojson):
    """Parse a GeoJSON polygon, normalize its SRID to the DB SRID and validate
    area and vertex count.

    Returns (polygon, None) on success or (None, Response) on error so callers
    can short-circuit with the DRF response.
    """
    if not polygon_geojson:
        return None, Response(
            {"error": "No polygon data provided"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        polygon = GEOSGeometry(str(polygon_geojson))
        if polygon.srid is None or polygon.srid == 0:
            polygon.srid = SRID_DOWNLOADED_DATA
        polygon.transform(SRID_DB)
    except Exception:
        logger.exception("Invalid polygon geometry: %s", polygon_geojson)
        return None, Response(
            {"error": "Invalid polygon shape"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if polygon.area > MAX_POLYGON_AREA_M2:
        return None, Response(
            {
                "error": f"Polygon area exceeds maximum allowed size ({MAX_POLYGON_AREA_M2 / 1_000_000} km²)"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    num_coords = (
        len(polygon.coords[0])
        if polygon.geom_type == "Polygon"
        else sum(len(ring) for ring in polygon.coords)
    )
    if num_coords > MAX_VERTICES:
        return None, Response(
            {
                "error": f"Polygon complexity exceeds maximum allowed vertices ({MAX_VERTICES})"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return polygon, None
