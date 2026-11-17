from pathlib import Path

import numpy as np
import rasterio


def write_rgba(path: Path | str, rgb: np.ndarray, valid: np.ndarray, profile: dict):
    profile = {
        **profile,
        "dtype": "uint8",
        "count": 4,
        "nodata": None,
        "photometric": "RGB",
        "alpha": "YES",
        "compress": "lzw",
    }
    for key in ("predictor", "blockxsize", "blockysize"):
        profile.pop(key, None)
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(rgb.astype(np.uint8), [1, 2, 3])
        dst.write(np.where(valid, 255, 0).astype(np.uint8), 4)
