"""Rasterize vulnerability and LCZ vector layers to colored GeoTIFF files.

Produces rasters ready for QGIS display with platform colors already applied:

- **Integer rasters** (LCZ, vegestrate): palette embedded via ``write_colormap``.
- **Float rasters** (vulnerability): a pre-colored RGB variant ``<name>_colors.tif``
  is generated in addition to the raw float, because QGIS does not load ``.qml``
  sidecars for remote rasters served via ``/vsicurl/``.

Usage:
    python manage.py generate_calque_rasters
    python manage.py generate_calque_rasters --calque vulnerability
    python manage.py generate_calque_rasters --calque lcz
    python manage.py generate_calque_rasters --calque vegestrate
"""

import logging
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np
import rasterio
from django.conf import settings
from django.contrib.gis.db.models import Union
from django.core.management import BaseCommand
from rasterio.enums import ColorInterp
from rasterio.features import rasterize

from iarbre_data.models import City, Lcz, Vulnerability
from iarbre_data.utils.database import load_geodataframe_from_db

logger = logging.getLogger(__name__)

RASTERS_DIR = Path(settings.MEDIA_ROOT) / "rasters"
TRANSPARENT = (0, 0, 0, 0)


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert ``#RRGGBB`` to an ``(R, G, B)`` tuple."""
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


# -- Platform palettes (mirrored from front/src/utils/*.ts) ------------------

# front/src/utils/climateZone.ts — CLIMATE_ZONE_MAP_COLOR_MAP
LCZ_PALETTE: dict[int, str] = {
    1: "#8C0000",  # Compact high-rise
    2: "#D10000",  # Compact mid-rise
    3: "#FF0000",  # Compact low-rise
    4: "#BF4D00",  # Open high-rise
    5: "#FA6600",  # Open mid-rise
    6: "#FF9955",  # Open low-rise
    7: "#FAEE05",  # Lightweight low-rise
    8: "#BCBCBC",  # Large low-rise
    9: "#FFCCAA",  # Sparsely built
    11: "#006A00",  # Dense trees (A)
    12: "#00AA00",  # Scattered trees (B)
    13: "#648525",  # Bush, scrub (C)
    14: "#B9DB79",  # Low plants (D)
    15: "#000000",  # Bare rock / paved (E)
    16: "#FBF7AE",  # Bare soil / sand (F)
    17: "#6A6AFF",  # Water (G)
}

# front/src/utils/vegetation.ts — VEGESTRATE_COLOR_MAP
VEGESTRATE_PALETTE: dict[int, str] = {
    1: "#C8D96F",  # herbacée
    2: "#3A9144",  # arbustive
    3: "#14452F",  # arborescente
}

# front/src/utils/vulnerability.ts — VULNERABILITY_COLOR_MAP
VULNERABILITY_STOPS: list[tuple[int, str]] = [
    (1, "#4474b5"),
    (2, "#75add1"),
    (3, "#aad9e9"),
    (4, "#5aaf7b"),
    (5, "#9cbf4e"),
    (6, "#d7e360"),
    (7, "#fdae60"),
    (8, "#f56c43"),
    (9, "#d73026"),
]

# Natural LCZ zones (A-G) → integer codes 11-17 (WUDAPT/OGC convention).
_LCZ_LETTERS = {"A": 11, "B": 12, "C": 13, "D": 14, "E": 15, "F": 16, "G": 17}


def _lcz_index_to_int(value: Any) -> int | None:
    """Convert an LCZ index (e.g. ``'1'``, ``'G'``) to an integer code."""
    if value is None:
        return None
    s = str(value).strip()
    if s in _LCZ_LETTERS:
        return _LCZ_LETTERS[s]
    try:
        return int(s)
    except (TypeError, ValueError):
        return None


# -- Raster I/O helpers ------------------------------------------------------


def _reference_grid() -> dict:
    """Read the plantability raster header (CRS, transform, shape)."""
    with rasterio.open(RASTERS_DIR / "plantability.tif") as src:
        return {
            "crs": src.crs,
            "transform": src.transform,
            "width": src.width,
            "height": src.height,
        }


def _metro_geometry():
    """Union of all city geometries (excluding the test city) — spatial filter."""
    return City.objects.exclude(code="38250").aggregate(union=Union("geometry"))[
        "union"
    ]


def _rasterize_field(
    queryset,
    field: str,
    dtype: Any,
    nodata: int | float,
    ref: dict,
    transform: Callable | None = None,
) -> np.ndarray:
    """Rasterize a queryset's ``field`` onto ``ref``'s grid."""
    gdf = load_geodataframe_from_db(queryset, ["id", field])
    cast = transform or (lambda v: v)
    shapes = [
        (geom, cast_val)
        for geom, raw in zip(gdf.geometry, gdf[field])
        if (cast_val := cast(raw)) is not None
    ]
    logger.info("Rasterizing %d features (field=%s)", len(shapes), field)
    return rasterize(
        shapes,
        out_shape=(ref["height"], ref["width"]),
        transform=ref["transform"],
        fill=nodata,
        dtype=dtype,
    )


def _write_geotiff(
    array: np.ndarray, path: Path, dtype: Any, nodata: int | float, ref: dict
) -> None:
    """Write a single-band LZW-compressed GeoTIFF aligned with ``ref``."""
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=ref["height"],
        width=ref["width"],
        count=1,
        dtype=dtype,
        crs=ref["crs"],
        transform=ref["transform"],
        nodata=nodata,
        compress="lzw",
    ) as dst:
        dst.write(array, 1)
    logger.info("Generated %s (%.1f MB)", path, path.stat().st_size / 1024**2)


def _embed_palette(raster_path: Path, palette: dict[int, str]) -> None:
    """Embed an indexed RGBA palette into an integer GeoTIFF band.

    Missing palette indices default to fully transparent so QGIS does not
    render unused values as solid black.
    """
    max_key = max(palette.keys())
    cmap = {
        i: ((*_hex_to_rgb(palette[i]), 255) if i in palette else TRANSPARENT)
        for i in range(max_key + 1)
    }
    with rasterio.open(raster_path, "r+") as dst:
        dst.write_colormap(1, cmap)
    logger.info("Embedded palette in %s", raster_path.name)


def _write_rgb_from_stops(
    float_path: Path,
    output_path: Path,
    stops: list[tuple[int, str]],
    nodata: float,
) -> None:
    """Render a float raster as a 3-band RGB GeoTIFF via linear color interpolation.

    Produces a file QGIS displays in color out-of-the-box, even when loaded
    remotely via ``/vsicurl/``.
    """
    values = np.array([s[0] for s in stops], dtype=np.float32)
    colors = np.array([_hex_to_rgb(s[1]) for s in stops], dtype=np.uint8)

    with rasterio.open(float_path) as src:
        data = src.read(1)
        profile = src.profile.copy()

    mask = data != nodata
    rgb = np.zeros((3, *data.shape), dtype=np.uint8)
    for i in range(3):
        rgb[i][mask] = np.clip(
            np.interp(data[mask], values, colors[:, i]), 0, 255
        ).astype(np.uint8)

    profile.update(
        dtype="uint8", count=3, nodata=None, photometric="RGB", compress="lzw"
    )
    profile.pop("predictor", None)
    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(rgb)
        dst.colorinterp = (ColorInterp.red, ColorInterp.green, ColorInterp.blue)
    logger.info(
        "Generated RGB preview %s (%.1f MB)",
        output_path,
        output_path.stat().st_size / 1024**2,
    )


# -- Calque processors -------------------------------------------------------
# All processors share the same signature so the dispatch dict stays trivial.


def generate_vulnerability(ref: dict, union) -> Path:
    """Rasterize vulnerability (float) and produce the RGB color variant."""
    nodata = -9999.0
    qs = Vulnerability.objects.filter(geometry__intersects=union)
    array = _rasterize_field(qs, "vulnerability_index_day", np.float32, nodata, ref)
    raw_path = RASTERS_DIR / "vulnerability.tif"
    _write_geotiff(array, raw_path, np.float32, nodata, ref)
    _write_rgb_from_stops(
        raw_path, RASTERS_DIR / "vulnerability_colors.tif", VULNERABILITY_STOPS, nodata
    )
    return raw_path


def generate_lcz(ref: dict, union) -> Path:
    """Rasterize LCZ (uint8) with the WUDAPT palette embedded."""
    qs = Lcz.objects.filter(geometry__intersects=union)
    array = _rasterize_field(
        qs, "lcz_index", np.uint8, 0, ref, transform=_lcz_index_to_int
    )
    path = RASTERS_DIR / "lcz.tif"
    _write_geotiff(array, path, np.uint8, 0, ref)
    _embed_palette(path, LCZ_PALETTE)
    return path


def apply_vegestrate_palette(ref: dict, union) -> Path:
    """Embed the vegestrate palette in the existing raster (no rasterization)."""
    path = RASTERS_DIR / "vegestrate_lyon_metropole_ir_02.tif"
    if not path.exists():
        raise ValueError(f"Raster not found: {path}")
    _embed_palette(path, VEGESTRATE_PALETTE)
    return path


CALQUES: dict[str, Callable[[dict, Any], Path]] = {
    "vulnerability": generate_vulnerability,
    "lcz": generate_lcz,
    "vegestrate": apply_vegestrate_palette,
}


# -- Command -----------------------------------------------------------------


class Command(BaseCommand):
    help = "Rasterize calques (vulnerability, LCZ, vegestrate) with platform colors."

    def add_arguments(self, parser):
        parser.add_argument(
            "--calque",
            choices=list(CALQUES.keys()),
            default=None,
            help="Process a single calque. If omitted, processes all.",
        )

    def handle(self, *args, **options):
        names = [options["calque"]] if options["calque"] else list(CALQUES.keys())
        ref = _reference_grid()
        union = _metro_geometry()

        for name in names:
            start = time.monotonic()
            path = CALQUES[name](ref, union)
            elapsed = time.monotonic() - start
            self.stdout.write(
                self.style.SUCCESS(f"  {name} -> {path} in {elapsed:.1f}s")
            )
