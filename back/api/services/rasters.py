"""Reading GeoTIFF rasters and encoding them as PNG images."""

import io
from pathlib import Path

import mercantile
import numpy as np
import rasterio
from django.conf import settings
from PIL import Image
from pyproj import Transformer
from rasterio.warp import Resampling
from rasterio.windows import from_bounds

TILE_SIZE = 256

# Height given to nodata pixels in the DEM-encoded tiles, rendered transparent
# by the front-end color ramp (any value below 0).
NODATA_HEIGHT = -1.0

WMS_RASTER_DIR = Path("rasters/WMS")
VEGETATION_HEIGHT_RASTER = "vegestrate_02_2023_elevation.tif"


def vegetation_height_raster() -> Path:
    return Path(settings.MEDIA_ROOT) / WMS_RASTER_DIR / VEGETATION_HEIGHT_RASTER


# --- Reading ------------------------------------------------------------------


def read_tile(
    raster_path: Path, tile: mercantile.Tile
) -> tuple[np.ndarray | None, float | None]:
    """Read a TILE_SIZE x TILE_SIZE window matching a web mercator tile.

    Returns ``(None, None)`` when the tile does not overlap the raster.
    """
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

        nodata = src.nodata
        if nodata is None:
            dtype = np.dtype(src.dtypes[0])
            info = np.finfo if np.issubdtype(dtype, np.floating) else np.iinfo
            nodata = info(dtype).max

        window = from_bounds(left, bottom, right, top, transform=src.transform)
        data = src.read(
            1,
            window=window,
            out_shape=(TILE_SIZE, TILE_SIZE),
            resampling=Resampling.nearest,
            boundless=True,
            fill_value=nodata,
        )
        return data, nodata


def sample_at_point(raster_path: Path, lng: float, lat: float) -> int | None:
    """Value of the first band at a WGS84 point, or None outside the raster
    or on nodata."""
    with rasterio.open(raster_path) as src:
        transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
        x, y = transformer.transform(lng, lat)
        b = src.bounds
        if x < b.left or x > b.right or y < b.bottom or y > b.top:
            return None
        value = int(next(src.sample([(x, y)]))[0])
        if src.nodata is not None and value == int(src.nodata):
            return None
        return value


# --- Encoding -----------------------------------------------------------------


def colorize(
    data: np.ndarray, color_map: dict[int, tuple[int, int, int, int]]
) -> np.ndarray:
    rgba_data = np.zeros((*data.shape, 4), dtype=np.uint8)
    for value, color in color_map.items():
        rgba_data[data == value] = color
    return rgba_data


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


def grayscale_image(data: np.ndarray, nodata) -> Image.Image:
    """Encode raw raster values as a grayscale ("LA") image, no color mapping.

    Pixel intensity is the raw band value (clipped to 0-255); nodata and NaN
    pixels are made fully transparent so the stream carries no color code.
    """
    arr = np.asarray(data)
    transparent = np.zeros(arr.shape, dtype=bool)
    if np.issubdtype(arr.dtype, np.floating):
        transparent |= np.isnan(arr)
    if nodata is not None:
        transparent |= arr == nodata

    gray = np.clip(np.nan_to_num(arr, nan=0.0), 0, 255).astype(np.uint8)
    alpha = np.where(transparent, 0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack([gray, alpha]), mode="LA")


def png_bytes(img: Image.Image) -> bytes:
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def empty_png(width: int = TILE_SIZE, height: int = TILE_SIZE) -> bytes:
    """A fully transparent PNG."""
    return png_bytes(Image.new("RGBA", (width, height), (0, 0, 0, 0)))


def rgb_image(src, window, width: int, height: int) -> Image.Image:
    """Encode the first three bands as an RGBA image, alpha from the dataset mask."""
    rgb = src.read(
        [1, 2, 3],
        window=window,
        out_shape=(3, height, width),
        resampling=Resampling.nearest,
    )
    alpha = src.dataset_mask(window=window, out_shape=(height, width))
    return Image.fromarray(np.dstack([*rgb, alpha]), mode="RGBA")


def render_wms_png(
    raster_path: Path,
    crs: str,
    bbox: tuple[float, float, float, float],
    width: int,
    height: int,
) -> bytes:
    """Render ``bbox`` (west, south, east, north, expressed in ``crs``) as a
    ``width`` x ``height`` PNG; transparent outside the raster.

    Rasters with 3+ bands are rendered as RGBA, single-band ones as raw
    grayscale values."""
    west, south, east, north = bbox
    with rasterio.open(raster_path) as src:
        transformer = Transformer.from_crs(crs, src.crs, always_xy=True)
        left, bottom = transformer.transform(west, south)
        right, top = transformer.transform(east, north)

        b = src.bounds
        if right < b.left or left > b.right or top < b.bottom or bottom > b.top:
            return empty_png(width, height)

        window = from_bounds(left, bottom, right, top, transform=src.transform)
        if src.count >= 3:
            img = rgb_image(src, window, width, height)
        else:
            data = src.read(
                1,
                window=window,
                out_shape=(height, width),
                resampling=Resampling.nearest,
            )
            img = grayscale_image(data, src.nodata)

    return png_bytes(img)
