import logging
import os
from pathlib import Path

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
            return self.encode_terrarium(data, nodata)
        return self.colorize(data, VEGESTRATE_COLOR_MAP)


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
