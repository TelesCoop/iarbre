import logging
import os
from pathlib import Path

import numpy as np
import rasterio
from django.conf import settings
from django.http import Http404
from pyproj import Transformer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.views.raster_tile_views import RasterTileView
from iarbre_data.utils.palettes import VEGESTRATE_COLOR_MAP

logger = logging.getLogger(__name__)

# Height given to nodata pixels in the DEM-encoded tiles, rendered transparent
# by the front-end color ramp (any value below 0).
NODATA_HEIGHT = -1.0


class VegetationHeightTileView(RasterTileView):
    """
    Serve vegetation raster data as {z}/{x}/{y} PNG tiles for MapLibre.
    Converts GeoTIFF to PNG tiles on-the-fly with proper georeferencing.
    """

    def raster_path(self, request) -> Path:
        return (
            Path(settings.MEDIA_ROOT)
            / "rasters/WMS"
            / "vegestrate_02_2023_elevation.tif"
        )

    def render(self, data, nodata, request):
        if request.query_params.get("kind", "class") == "raw":
            rgba_data = np.zeros((*data.shape, 4), dtype=np.uint8)
            self._encode_terrarium(data, nodata, rgba_data)
            return rgba_data
        return self.colorize(data, VEGESTRATE_COLOR_MAP)

    @staticmethod
    def _encode_terrarium(data, nodata, rgba_data):
        """Encode heights in-place into `rgba_data` as terrarium RGB.

        Decoded client-side as `R * 256 + G + B / 256 - 32768`, so the front-end
        can classify heights itself instead of receiving pre-colored pixels.
        """
        heights = data.astype(np.float64)
        if nodata is not None:
            heights[data == nodata] = NODATA_HEIGHT
        shifted = heights + 32768.0
        rgba_data[..., 0] = (shifted // 256).astype(np.uint8)
        rgba_data[..., 1] = (shifted % 256).astype(np.uint8)
        rgba_data[..., 2] = ((shifted % 1) * 256).astype(np.uint8)
        rgba_data[..., 3] = 255


class VegetationHeightAtPointView(APIView):
    def get(self, request):
        try:
            lat = float(request.query_params["lat"])
            lng = float(request.query_params["lng"])
        except (KeyError, ValueError):
            return Response(
                {"error": "lat and lng required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        raster_path = os.path.join(
            settings.MEDIA_ROOT, "rasters/WMS", "vegestrate_02_2023_elevation.tif"
        )
        if not os.path.exists(raster_path):
            raise Http404("Vegetation raster not found")

        try:
            with rasterio.open(raster_path) as src:
                transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
                x, y = transformer.transform(lng, lat)
                b = src.bounds
                if x < b.left or x > b.right or y < b.bottom or y > b.top:
                    return Response({"height": None})
                value = int(next(src.sample([(x, y)]))[0])
                if src.nodata is not None and value == int(src.nodata):
                    return Response({"height": None})
                return Response({"height": value})
        except Exception:
            logger.exception("Error reading vegetation height at %s, %s", lat, lng)
            return Response({"height": None})
