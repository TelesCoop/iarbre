"""WMS layers: discovered from the GeoTIFFs stored in ``media/rasters/WMS``."""

from pathlib import Path

import rasterio
from django.conf import settings
from django.core.cache import cache
from pyproj import Transformer

WMS_RASTER_DIR = "rasters/WMS"


def discover_layers() -> dict:
    """Discover the available WMS layers by globbing ``media/rasters/WMS/*.tif``.

    Each ``<name>.tif`` becomes the layer ``iarbre:<name>``. The layer list is
    driven by what is on disk, not by a static registry.
    """
    wms_root = Path(settings.MEDIA_ROOT) / WMS_RASTER_DIR
    if not wms_root.is_dir():
        return {}
    return {
        f"iarbre:{tif.stem}": {"title": tif.stem, "path": tif}
        for tif in sorted(wms_root.glob("*.tif"))
    }


def layer_bounds_wgs84(name: str, raster_path: Path) -> tuple[float, ...]:
    """(west, south, east, north) of a layer in EPSG:4326, cached forever."""
    bounds_key = f"wms:bounds:{name}"
    bounds = cache.get(bounds_key)
    if bounds is None:
        with rasterio.open(raster_path) as src:
            t = Transformer.from_crs(src.crs, "EPSG:4326", always_xy=True)
            west, south = t.transform(src.bounds.left, src.bounds.bottom)
            east, north = t.transform(src.bounds.right, src.bounds.top)
        bounds = (west, south, east, north)
        cache.set(bounds_key, bounds, timeout=None)
    return bounds
