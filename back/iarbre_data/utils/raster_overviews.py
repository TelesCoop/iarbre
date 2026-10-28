import os
import tempfile
from pathlib import Path

import rasterio
from rasterio.enums import Resampling

MIN_OVERVIEW_SIZE = 256


def overview_factors(width: int, height: int) -> list[int]:
    factors = []
    factor = 2
    while min(width, height) // factor >= MIN_OVERVIEW_SIZE:
        factors.append(factor)
        factor *= 2
    return factors


def ovr_path(path: Path) -> Path:
    return path.with_name(path.name + ".ovr")


def overviews_up_to_date(path: Path) -> bool:
    ovr = ovr_path(path)
    return ovr.exists() and ovr.stat().st_mtime >= path.stat().st_mtime


def build_overviews(path: Path, force: bool = False) -> bool:
    if not force and overviews_up_to_date(path):
        return False
    with rasterio.open(path) as src:
        factors = overview_factors(src.width, src.height)
    if not factors:
        return False

    with tempfile.TemporaryDirectory(dir=path.parent, prefix=".ovr_") as tmp_dir:
        link = Path(tmp_dir) / path.name
        link.symlink_to(path.resolve())
        with rasterio.Env(
            TIFF_USE_OVR=True, COMPRESS_OVERVIEW="DEFLATE", BIGTIFF_OVERVIEW="IF_SAFER"
        ):
            with rasterio.open(link, "r+") as src:
                src.build_overviews(factors, Resampling.nearest)
        os.replace(ovr_path(link), ovr_path(path))
    return True
