import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

import rasterio
from rasterio.enums import Resampling

from iarbre_data.utils.raster_overviews import overview_factors


def hour_raster_path(src_path: Path, hour: int) -> Path:
    return src_path.parent / src_path.stem / f"{src_path.stem}_h{hour:02d}.tif"


def is_up_to_date(src_path: Path, dst_path: Path) -> bool:
    return dst_path.exists() and dst_path.stat().st_mtime >= src_path.stat().st_mtime


def extract_band(src_path: Path, band: int, dst_path: Path) -> None:
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(suffix=".tif.part", dir=dst_path.parent)
    os.close(fd)
    try:
        with rasterio.open(src_path) as src:
            profile = src.profile
            profile.update(count=1, interleave="band")
            factors = overview_factors(src.width, src.height)
            with rasterio.open(tmp_name, "w", **profile) as dst:
                for _, window in src.block_windows(band):
                    dst.write(src.read(band, window=window), 1, window=window)
                if factors:
                    dst.build_overviews(factors, Resampling.nearest)
                    dst.update_tags(ns="rio_overview", resampling="nearest")
        os.replace(tmp_name, dst_path)
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)


def split_hours(src_path: Path, force: bool = False) -> Iterator[tuple[Path, bool]]:
    with rasterio.open(src_path) as src:
        band_count = src.count
    for hour in range(band_count):
        dst_path = hour_raster_path(src_path, hour)
        if not force and is_up_to_date(src_path, dst_path):
            yield dst_path, False
            continue
        extract_band(src_path, hour + 1, dst_path)
        yield dst_path, True
