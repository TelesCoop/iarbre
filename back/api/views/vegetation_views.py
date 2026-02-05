import io
import logging
import os

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
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class VegetationTileView(APIView):
    """
    Serve vegetation raster data as {z}/{x}/{y} PNG tiles for MapLibre.
    Converts GeoTIFF to PNG tiles on-the-fly with proper georeferencing.
    """

    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, z, x, y):
        """Generate a raster tile from the vegetation GeoTIFF."""
        zoom = int(z)
        tile_x = int(x)
        tile_y = int(y)

        raster_path = os.path.join(
            settings.MEDIA_ROOT,
            "rasters",
            "merged_fullmetropole_08.tif",
        )

        if not os.path.exists(raster_path):
            raise Http404("Vegetation raster file not found")

        try:
            tile = mercantile.Tile(tile_x, tile_y, zoom)
            bounds_wgs84 = mercantile.bounds(tile)

            with rasterio.open(raster_path) as src:
                transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
                left, bottom = transformer.transform(
                    bounds_wgs84.west, bounds_wgs84.south
                )
                right, top = transformer.transform(
                    bounds_wgs84.east, bounds_wgs84.north
                )

                raster_bounds = src.bounds
                if (
                    right < raster_bounds.left
                    or left > raster_bounds.right
                    or top < raster_bounds.bottom
                    or bottom > raster_bounds.top
                ):
                    return self._empty_tile()

                try:
                    window = from_bounds(
                        left, bottom, right, top, transform=src.transform
                    )

                    data = src.read(
                        1,
                        window=window,
                        out_shape=(256, 256),
                        resampling=Resampling.bilinear,
                    )

                    color_map = {
                        0: (0, 0, 0, 0),
                        1: (157, 193, 131, 255),
                        2: (88, 129, 87, 255),
                        3: (45, 90, 22, 255),
                    }

                    h, w = data.shape
                    rgba_data = np.zeros((h, w, 4), dtype=np.uint8)

                    for value, color in color_map.items():
                        mask = data == value
                        rgba_data[mask] = color

                    img = Image.fromarray(rgba_data, mode="RGBA")

                    buffer = io.BytesIO()
                    img.save(buffer, format="PNG")
                    buffer.seek(0)

                    return HttpResponse(buffer.getvalue(), content_type="image/png")

                except Exception:
                    logger.exception("Window error for tile %s/%s/%s", z, x, y)
                    return self._empty_tile()

        except Exception:
            logger.exception("Error generating vegetation tile %s/%s/%s", z, x, y)
            return self._empty_tile()

    def _empty_tile(self):
        """Return a transparent 256x256 PNG."""
        img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return HttpResponse(buffer.getvalue(), content_type="image/png")
