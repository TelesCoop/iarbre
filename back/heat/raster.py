import os
import tempfile
from pathlib import Path

import rasterio
from rasterio.enums import Resampling

OVERVIEW_FACTORS = [2, 4, 8, 16, 32, 64]


def hour_raster_path(src_path: Path, hour: int) -> Path:
    """Path of the single-band GeoTIFF holding ``hour`` of ``src_path``."""
    return src_path.parent / src_path.stem / f"{src_path.stem}_h{hour:02d}.tif"


def is_up_to_date(src_path: Path, dst_path: Path) -> bool:
    return dst_path.exists() and dst_path.stat().st_mtime >= src_path.stat().st_mtime


def extract_band(src_path: Path, band: int, dst_path: Path) -> None:
    """Write ``band`` of ``src_path`` as a single-band GeoTIFF at ``dst_path``."""
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(suffix=".tif.part", dir=dst_path.parent)
    os.close(fd)
    try:
        with rasterio.open(src_path) as src:
            profile = src.profile
            profile.update(count=1, interleave="band")
            with rasterio.open(tmp_name, "w", **profile) as dst:
                for _, window in src.block_windows(band):
                    dst.write(src.read(band, window=window), 1, window=window)
                dst.build_overviews(OVERVIEW_FACTORS, Resampling.nearest)
                dst.update_tags(ns="rio_overview", resampling="nearest")
        os.replace(tmp_name, dst_path)
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
