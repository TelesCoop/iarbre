import io
import logging
from pathlib import Path

import mercantile
import numpy as np
import rasterio
from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from PIL import Image
from pyproj import Transformer
from rasterio.warp import Resampling
from rasterio.windows import from_bounds
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from api.constants import (
    HEAT_FILES,
    HOURLY_HEAT_LAYERS,
    PET_INDEX_COLOR_MAP,
    SUN_EXPOSURE_COLOR_BINS,
)
from heat.raster import hour_raster_path, is_up_to_date

logger = logging.getLogger(__name__)

HEAT_HOURS = range(25)


class HeatTileView(APIView):
    """
    Serve heat raster data as {z}/{x}/{y} PNG tiles for MapLibre.

        GET /api/tiles/heat/{z}/{x}/{y}.png?mode=pet_index&hour=14
        GET /api/tiles/heat/{z}/{x}/{y}.png?mode=sun_exposure
    """

    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, z, x, y):
        mode = request.query_params.get("mode", "pet_index")
        if mode not in HEAT_FILES:
            raise ValidationError({"mode": f"Must be one of {', '.join(HEAT_FILES)}."})

        raster_path = Path(settings.MEDIA_ROOT) / "rasters/WMS" / HEAT_FILES[mode]
        if mode in HOURLY_HEAT_LAYERS:
            raster_path = self._hour_path(raster_path, request.query_params)

        if not raster_path.exists():
            raise Http404("Heat raster file not found")

        try:
            data, nodata = self._read_tile(raster_path, mercantile.Tile(x, y, z))
        except Exception:
            logger.exception("Error generating heat tile %s/%s/%s", z, x, y)
            return self._empty_tile()
        if data is None:
            return self._empty_tile()

        rgba_data = np.zeros((*data.shape, 4), dtype=np.uint8)
        valid = data != nodata if nodata is not None else np.ones(data.shape, bool)
        if mode == "pet_index":
            for value, color in PET_INDEX_COLOR_MAP.items():
                rgba_data[valid & (data == value)] = color
        else:
            for min_value, color in SUN_EXPOSURE_COLOR_BINS:
                rgba_data[valid & (data >= min_value)] = color

        return self._png_response(Image.fromarray(rgba_data, mode="RGBA"))

    @staticmethod
    def _hour_path(raster_path: Path, query_params) -> Path:
        try:
            hour = int(query_params.get("hour", ""))
        except ValueError:
            raise ValidationError({"hour": "Must be an integer."})
        if hour not in HEAT_HOURS:
            raise ValidationError(
                {"hour": f"Must be between {HEAT_HOURS[0]} and {HEAT_HOURS[-1]}."}
            )
        hour_path = hour_raster_path(raster_path, hour)
        if not is_up_to_date(raster_path, hour_path):
            raise Http404(f"File not found: {hour_path.name}.")
        return hour_path

    @staticmethod
    def _read_tile(raster_path: Path, tile: mercantile.Tile):
        bounds_wgs84 = mercantile.bounds(tile)
        with rasterio.open(raster_path) as src:
            transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
            left, bottom = transformer.transform(bounds_wgs84.west, bounds_wgs84.south)
            right, top = transformer.transform(bounds_wgs84.east, bounds_wgs84.north)

            raster_bounds = src.bounds
            if (
                right < raster_bounds.left
                or left > raster_bounds.right
                or top < raster_bounds.bottom
                or bottom > raster_bounds.top
            ):
                return None, None

            window = from_bounds(left, bottom, right, top, transform=src.transform)
            data = src.read(
                1,
                window=window,
                out_shape=(256, 256),
                resampling=Resampling.nearest,
                boundless=True,
                fill_value=src.nodata or 0,
            )
            return data, src.nodata

    def _empty_tile(self):
        """Return a transparent 256x256 PNG."""
        return self._png_response(Image.new("RGBA", (256, 256), (0, 0, 0, 0)))

    @staticmethod
    def _png_response(img: Image.Image) -> HttpResponse:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return HttpResponse(buffer.getvalue(), content_type="image/png")
