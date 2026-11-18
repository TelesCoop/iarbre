"""Parsing and validation of user-drawn polygons."""

import logging

from django.contrib.gis.geos import GEOSGeometry

from iarbre_data.settings import SRID_DB, SRID_DOWNLOADED_DATA

logger = logging.getLogger(__name__)

MAX_POLYGON_AREA_M2 = 5_000_000
# Accommodates the circle tool (64-segment polygon) plus richer hand-drawn
# polygons, while still bounding the cost of the spatial query.
MAX_VERTICES = 100


class InvalidPolygon(ValueError):
    """The polygon sent by the client is missing, malformed or too large.

    The message is meant to be returned to the client.
    """


def parse_polygon(polygon_geojson):
    """Parse a GeoJSON polygon, normalize its SRID to the DB SRID and validate
    area and vertex count.

    Raises ``InvalidPolygon`` when the polygon is not acceptable.
    """
    if not polygon_geojson:
        raise InvalidPolygon("No polygon data provided")

    try:
        polygon = GEOSGeometry(str(polygon_geojson))
        if polygon.srid is None or polygon.srid == 0:
            polygon.srid = SRID_DOWNLOADED_DATA
        polygon.transform(SRID_DB)
    except Exception as exc:
        # A malformed client polygon is a client error, not a server fault.
        logger.exception("Invalid polygon geometry: %s", polygon_geojson)
        raise InvalidPolygon("Invalid polygon shape") from exc

    if polygon.area > MAX_POLYGON_AREA_M2:
        message = (
            f"Polygon area {polygon.area} exceeds maximum allowed size "
            f"({MAX_POLYGON_AREA_M2 / 1_000_000} km²)"
        )
        logger.error(message)
        raise InvalidPolygon(message)

    num_coords = (
        len(polygon.coords[0])
        if polygon.geom_type == "Polygon"
        else sum(len(ring) for ring in polygon.coords)
    )
    if num_coords > MAX_VERTICES:
        raise InvalidPolygon(
            f"Polygon complexity exceeds maximum allowed vertices ({MAX_VERTICES})"
        )

    return polygon
