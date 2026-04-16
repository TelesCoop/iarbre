"""Rasterize Vulnerability and LCZ vector layers to GeoTIFF files.

Uses the plantability raster as a spatial reference (bounds, resolution, CRS)
to produce aligned outputs suitable for overlay in QGIS. Platform colors
are embedded (palette) for integer rasters, or written as a sidecar .qml
style file for float rasters, so QGIS displays them styled out-of-the-box.

Usage:
    python manage.py generate_calque_rasters
    python manage.py generate_calque_rasters --calque vulnerability
    python manage.py generate_calque_rasters --calque lcz
    python manage.py generate_calque_rasters --calque vegestrate
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
import rasterio
from django.conf import settings
from django.contrib.gis.db.models import Union
from django.core.management import BaseCommand
from rasterio.features import rasterize

from iarbre_data.models import City, Lcz, Vulnerability
from iarbre_data.utils.database import load_geodataframe_from_db

logger = logging.getLogger(__name__)

RASTERS_DIR = Path(settings.MEDIA_ROOT) / "rasters"
REFERENCE_RASTER = "plantability.tif"


# -- Platform palettes (mirrored from front/src/utils/*.ts) ------------------


def _hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    """Convert ``#RRGGBB`` to an ``(R, G, B, alpha)`` tuple."""
    hex_color = hex_color.lstrip("#")
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
        alpha,
    )


TRANSPARENT = (0, 0, 0, 0)

# front/src/utils/climateZone.ts — CLIMATE_ZONE_MAP_COLOR_MAP
LCZ_COLORMAP: dict[int, tuple[int, int, int, int]] = {
    0: TRANSPARENT,  # nodata
    1: _hex_to_rgba("#8C0000"),  # Compact high-rise
    2: _hex_to_rgba("#D10000"),  # Compact mid-rise
    3: _hex_to_rgba("#FF0000"),  # Compact low-rise
    4: _hex_to_rgba("#BF4D00"),  # Open high-rise
    5: _hex_to_rgba("#FA6600"),  # Open mid-rise
    6: _hex_to_rgba("#FF9955"),  # Open low-rise
    7: _hex_to_rgba("#FAEE05"),  # Lightweight low-rise
    8: _hex_to_rgba("#BCBCBC"),  # Large low-rise
    9: _hex_to_rgba("#FFCCAA"),  # Sparsely built
    11: _hex_to_rgba("#006A00"),  # Dense trees (A)
    12: _hex_to_rgba("#00AA00"),  # Scattered trees (B)
    13: _hex_to_rgba("#648525"),  # Bush, scrub (C)
    14: _hex_to_rgba("#B9DB79"),  # Low plants (D)
    15: _hex_to_rgba("#000000"),  # Bare rock / paved (E)
    16: _hex_to_rgba("#FBF7AE"),  # Bare soil / sand (F)
    17: _hex_to_rgba("#6A6AFF"),  # Water (G)
}

# front/src/utils/vegetation.ts — VEGESTRATE_COLOR_MAP
# Raster class IDs (1=herbacee, 2=arbustif, 3=arborescent) follow
# back/vegetation/management/commands/add_vegestrate_data.py
VEGESTRATE_COLORMAP: dict[int, tuple[int, int, int, int]] = {
    0: TRANSPARENT,
    1: _hex_to_rgba("#C8D96F"),  # herbacée
    2: _hex_to_rgba("#3A9144"),  # arbustive
    3: _hex_to_rgba("#14452F"),  # arborescente
}

# front/src/utils/vulnerability.ts — VULNERABILITY_COLOR_MAP
# Continuous float values 1-9; applied via .qml pseudocolor sidecar.
VULNERABILITY_STOPS: list[tuple[int, str, str]] = [
    (1, "#4474b5", "1 — aucune"),
    (2, "#75add1", "2 — très faible"),
    (3, "#aad9e9", "3 — faible"),
    (4, "#5aaf7b", "4 — faible à moyenne"),
    (5, "#9cbf4e", "5 — moyenne"),
    (6, "#d7e360", "6 — moyenne à élevée"),
    (7, "#fdae60", "7 — élevée"),
    (8, "#f56c43", "8 — très élevée"),
    (9, "#d73026", "9 — critique"),
]


# -- LCZ index normalisation -------------------------------------------------


# Natural zones A-G → codes 11-17 (WUDAPT/OGC-LCZ convention: 10 + letter rank).
LCZ_LETTER_TO_CODE = {"A": 11, "B": 12, "C": 13, "D": 14, "E": 15, "F": 16, "G": 17}


def _lcz_index_to_int(value: Any) -> int | None:
    """Convert an LCZ index (e.g. ``'1'``, ``'10'``, ``'A'``, ``'G'``) to an int code."""
    if value is None:
        return None
    value = str(value).strip()
    if value in LCZ_LETTER_TO_CODE:
        return LCZ_LETTER_TO_CODE[value]
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# -- Style application -------------------------------------------------------


def _apply_colormap(raster_path: Path, colormap: dict) -> None:
    """Embed a GDAL colormap (palette) into an integer GeoTIFF.

    Missing palette indices are filled with a fully transparent entry so
    QGIS does not render them as solid black.
    """
    max_key = max(colormap.keys())
    full = {i: colormap.get(i, TRANSPARENT) for i in range(max_key + 1)}
    with rasterio.open(raster_path, "r+") as dst:
        dst.write_colormap(1, full)
    logger.info("Embedded colormap in %s", raster_path.name)


def _apply_qml_sidecar(raster_path: Path, stops: list[tuple[int, str, str]]) -> None:
    """Write a QGIS ``.qml`` pseudocolor ramp alongside the raster."""
    items = "\n".join(
        f'        <item alpha="255" color="{color}" label="{label}" value="{value}"/>'
        for value, color, label in stops
    )
    qml = (
        "<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>\n"
        '<qgis version="3.0">\n'
        "  <pipe>\n"
        '    <rasterrenderer type="singlebandpseudocolor" band="1" opacity="1">\n'
        "      <rastershader>\n"
        '        <colorrampshader colorRampType="INTERPOLATED" classificationMode="1">\n'
        f"{items}\n"
        "        </colorrampshader>\n"
        "      </rastershader>\n"
        "    </rasterrenderer>\n"
        "  </pipe>\n"
        "</qgis>\n"
    )
    qml_path = raster_path.with_suffix(".qml")
    qml_path.write_text(qml, encoding="utf-8")
    logger.info("Wrote %s", qml_path.name)


# -- Rasterization helpers ---------------------------------------------------


def _reference_grid() -> dict:
    """Read the plantability raster to get the reference grid parameters."""
    with rasterio.open(RASTERS_DIR / REFERENCE_RASTER) as src:
        return {
            "crs": src.crs,
            "transform": src.transform,
            "width": src.width,
            "height": src.height,
        }


def _all_cities_union():
    """Metropolitan area used as the spatial filter (test city excluded)."""
    return City.objects.exclude(code="38250").aggregate(union=Union("geometry"))[
        "union"
    ]


def _rasterize_queryset(
    queryset,
    value_field: str,
    dtype: Any,
    nodata: int | float,
    ref: dict,
    value_transform: Callable | None = None,
) -> np.ndarray:
    """Rasterize a vector queryset into a numpy array aligned with ``ref``."""
    gdf = load_geodataframe_from_db(queryset, ["id", value_field])
    if gdf.empty:
        raise ValueError(f"No data found for field {value_field!r}")

    shapes = []
    for geom, val in zip(gdf.geometry, gdf[value_field]):
        if value_transform is not None:
            val = value_transform(val)
        if val is None:
            continue
        shapes.append((geom, val))

    logger.info("Rasterizing %d features (field=%s)", len(shapes), value_field)
    return rasterize(
        shapes,
        out_shape=(ref["height"], ref["width"]),
        transform=ref["transform"],
        fill=nodata,
        dtype=dtype,
    )


def _write_geotiff(
    array: np.ndarray,
    output_path: Path,
    dtype: Any,
    nodata: int | float,
    ref: dict,
) -> None:
    """Write a 2D numpy array as a LZW-compressed GeoTIFF aligned with ``ref``."""
    with rasterio.open(
        output_path,
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
    size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info("Generated %s (%.1f MB)", output_path, size_mb)


# -- Calque definitions ------------------------------------------------------


@dataclass(frozen=True)
class RasterizeConfig:
    """Rasterization source: build a new GeoTIFF from a Django queryset."""

    queryset_fn: Callable
    value_field: str
    dtype: Any
    nodata: int | float
    value_transform: Callable | None = None


@dataclass(frozen=True)
class ExistingFileConfig:
    """Existing-file source: apply a style to a GeoTIFF already on disk."""

    filename: str


@dataclass(frozen=True)
class Calque:
    name: str
    source: RasterizeConfig | ExistingFileConfig
    # Style strategy: either a paletted colormap (integer rasters) or a .qml
    # pseudocolor sidecar (float rasters).
    colormap: dict | None = None
    qml_stops: list[tuple[int, str, str]] | None = None

    @property
    def output_path(self) -> Path:
        if isinstance(self.source, ExistingFileConfig):
            return RASTERS_DIR / self.source.filename
        return RASTERS_DIR / f"{self.name}.tif"

    def apply_style(self) -> None:
        if self.colormap is not None:
            _apply_colormap(self.output_path, self.colormap)
        elif self.qml_stops is not None:
            _apply_qml_sidecar(self.output_path, self.qml_stops)


CALQUES: dict[str, Calque] = {
    "vulnerability": Calque(
        name="vulnerability",
        source=RasterizeConfig(
            queryset_fn=lambda union: Vulnerability.objects.filter(
                geometry__intersects=union
            ),
            value_field="vulnerability_index_day",
            dtype=np.float32,
            nodata=-9999.0,
        ),
        qml_stops=VULNERABILITY_STOPS,
    ),
    "lcz": Calque(
        name="lcz",
        source=RasterizeConfig(
            queryset_fn=lambda union: Lcz.objects.filter(geometry__intersects=union),
            value_field="lcz_index",
            dtype=np.uint8,
            nodata=0,  # 0 is unused by LCZ codes (1-9, 11-17)
            value_transform=_lcz_index_to_int,
        ),
        colormap=LCZ_COLORMAP,
    ),
    "vegestrate": Calque(
        name="vegestrate",
        source=ExistingFileConfig(filename="vegestrate_lyon_metropole_ir_02.tif"),
        colormap=VEGESTRATE_COLORMAP,
    ),
}


# -- Command -----------------------------------------------------------------


def process_calque(calque: Calque, ref: dict | None = None, union=None) -> Path:
    """Generate (or re-style) the GeoTIFF for a given calque."""
    source = calque.source
    if isinstance(source, RasterizeConfig):
        assert ref is not None and union is not None
        array = _rasterize_queryset(
            source.queryset_fn(union),
            source.value_field,
            source.dtype,
            source.nodata,
            ref,
            source.value_transform,
        )
        _write_geotiff(array, calque.output_path, source.dtype, source.nodata, ref)
    else:
        if not calque.output_path.exists():
            raise ValueError(f"Raster not found: {calque.output_path}")

    calque.apply_style()
    return calque.output_path


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
        needs_rasterize = any(
            isinstance(CALQUES[n].source, RasterizeConfig) for n in names
        )
        ref = _reference_grid() if needs_rasterize else None
        union = _all_cities_union() if needs_rasterize else None

        for name in names:
            calque = CALQUES[name]
            start = time.monotonic()
            path = process_calque(calque, ref=ref, union=union)
            elapsed = time.monotonic() - start
            self.stdout.write(
                self.style.SUCCESS(f"  {name} -> {path} in {elapsed:.1f}s")
            )
