import io
import logging
from pathlib import Path

import mercantile
import numpy as np
import rasterio
from django.http import Http404, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from PIL import Image
from pyproj import Transformer
from rasterio.warp import Resampling
from rasterio.windows import from_bounds
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

TILE_SIZE = 256

# Height given to nodata pixels in the DEM-encoded tiles, rendered transparent
# by the front-end color ramp (any value below 0).
NODATA_HEIGHT = -1.0


def read_tile(
    raster_path: Path, tile: mercantile.Tile
) -> tuple[np.ndarray | None, float | None]:
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
            out_shape=(TILE_SIZE, TILE_SIZE),
            resampling=Resampling.nearest,
            boundless=True,
            fill_value=src.nodata or 0,
        )
        return data, src.nodata


class RasterTileView(APIView):
    def raster_path(self, request) -> Path:
        raise NotImplementedError

    def render(self, data: np.ndarray, nodata, request) -> np.ndarray:
        raise NotImplementedError

    @staticmethod
    def colorize(
        data: np.ndarray, color_map: dict[int, tuple[int, int, int, int]]
    ) -> np.ndarray:
        rgba_data = np.zeros((*data.shape, 4), dtype=np.uint8)
        for value, color in color_map.items():
            rgba_data[data == value] = color
        return rgba_data

    @staticmethod
    def encode_terrarium(data: np.ndarray, nodata) -> np.ndarray:
        """Encode values as terrarium RGB.

        Decoded client-side as `R * 256 + G + B / 256 - 32768`, so the front-end
        can classify values itself instead of receiving pre-colored pixels.
        """
        values = data.astype(np.float64)
        if nodata is not None:
            values[data == nodata] = NODATA_HEIGHT
        shifted = values + 32768.0
        rgba_data = np.zeros((*data.shape, 4), dtype=np.uint8)
        rgba_data[..., 0] = (shifted // 256).astype(np.uint8)
        rgba_data[..., 1] = (shifted % 256).astype(np.uint8)
        rgba_data[..., 2] = ((shifted % 1) * 256).astype(np.uint8)
        rgba_data[..., 3] = 255
        return rgba_data

    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, z, x, y):
        raster_path = self.raster_path(request)
        if not raster_path.exists():
            raise Http404("Raster file not found")

        try:
            data, nodata = read_tile(
                raster_path, mercantile.Tile(int(x), int(y), int(z))
            )
            if data is None:
                return self._empty_tile()
            rgba_data = self.render(data, nodata, request)
        except Exception:
            logger.exception("Error generating raster tile %s/%s/%s", z, x, y)
            return self._empty_tile()

        return self._png_response(Image.fromarray(rgba_data, mode="RGBA"))

    def _empty_tile(self):
        """Return a transparent 256x256 PNG."""
        return self._png_response(
            Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        )

    @staticmethod
    def _png_response(img: Image.Image) -> HttpResponse:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return HttpResponse(buffer.getvalue(), content_type="image/png")
