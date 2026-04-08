"""Helpers to query the COSIA-derived soil occupancy raster at a given point."""

import logging
import os
from typing import Optional, Tuple

import rasterio
from django.conf import settings
from pyproj import Transformer

from api.constants import (
    SOIL_OCCUPANCY_CLASSES,
    SOIL_OCCUPANCY_RASTER_PATH,
)
from iarbre_data.settings import SRID_DOWNLOADED_DATA

logger = logging.getLogger(__name__)


class SoilOccupancyRasterNotFound(Exception):
    """Raised when the soil occupancy raster file is missing from MEDIA_ROOT."""


def _resolve_raster_path() -> str:
    return os.path.join(settings.MEDIA_ROOT, SOIL_OCCUPANCY_RASTER_PATH)


def _get_class_info(class_id: int) -> dict:
    """Return the label/code for a raster class id, or an 'unknown' marker."""
    class_info = SOIL_OCCUPANCY_CLASSES.get(class_id)
    if class_info is None:
        return {"code": "unknown", "label": None}
    return class_info


def sample_soil_occupancy_at_point(longitude: float, latitude: float) -> Optional[dict]:
    """Sample the COSIA raster at a WGS84 (lng, lat) coordinate.

    Returns a dict with the class id, code and label, or None if the point
    lies outside the raster or on a nodata pixel.
    """
    raster_path = _resolve_raster_path()
    if not os.path.exists(raster_path):
        raise SoilOccupancyRasterNotFound(
            f"Soil occupancy raster not found at {raster_path}"
        )

    with rasterio.open(raster_path) as src:
        x, y = _transform_to_raster_crs(longitude, latitude, src.crs)

        left, bottom, right, top = src.bounds
        if not (left <= x <= right and bottom <= y <= top):
            return None

        sampled_values = next(src.sample([(x, y)]), None)
        if sampled_values is None or len(sampled_values) == 0:
            return None

        raw_value = sampled_values[0]
        if src.nodata is not None and raw_value == src.nodata:
            return None

        class_id = int(raw_value)
        class_info = _get_class_info(class_id)

        return {
            "class_id": class_id,
            "code": class_info["code"],
            "label": class_info["label"],
        }


def _transform_to_raster_crs(
    longitude: float, latitude: float, raster_crs
) -> Tuple[float, float]:
    """Project a WGS84 (lng, lat) point into the raster native CRS."""
    if raster_crs is None:
        raise ValueError("Soil occupancy raster has no CRS defined")

    source_crs = f"EPSG:{SRID_DOWNLOADED_DATA}"
    target_crs = raster_crs.to_string()
    if target_crs == source_crs:
        return longitude, latitude

    transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
    return transformer.transform(longitude, latitude)
