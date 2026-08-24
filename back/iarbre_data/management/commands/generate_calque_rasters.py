"""Rasterize calque vector layers to colored GeoTIFF files.

Produces rasters ready for QGIS display with platform colors already applied:

To add a new model, add colormap in back/iarbre_data/utils/palettes.py and details in back/iarbre_data/utils/calque_config.py.

Usage:
    python manage.py generate_calque_rasters
    python manage.py generate_calque_rasters --model vulnerability
    python manage.py generate_calque_rasters --model lcz
    python manage.py generate_calque_rasters --model vegestrate
    python manage.py generate_calque_rasters --model biosphere
"""

import logging
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np
import rasterio
from django.apps import apps
from django.conf import settings
from django.contrib.gis.db.models import Union
from django.core.management import BaseCommand
from rasterio.enums import ColorInterp
from rasterio.features import rasterize

from iarbre_data.models import City
from iarbre_data.utils.calque_config import CALQUE_REGISTRY, CalqueConfig
from iarbre_data.utils.database import load_geodataframe_from_db

logger = logging.getLogger(__name__)

RASTERS_DIR = Path(settings.MEDIA_ROOT) / "rasters/WMS"
TRANSPARENT = (0, 0, 0, 0)


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _reference_grid() -> dict:
    with rasterio.open(RASTERS_DIR / "plantability.tif") as src:
        return {
            "crs": src.crs,
            "transform": src.transform,
            "width": src.width,
            "height": src.height,
        }


def _metro_geometry():
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
    gdf = load_geodataframe_from_db(queryset, ["id", field])
    if gdf.empty:
        raise ValueError(
            f"No objects found for field={field!r} — the table may be empty "
            "or no geometry intersects the metro area."
        )
    cast = transform or (lambda v: v)
    shapes = [
        (geom, cast_val)
        for geom, raw in zip(gdf.geometry, gdf[field])
        if (cast_val := cast(raw)) is not None
    ]
    if not shapes:
        raise ValueError(
            f"No rasterizable values for field={field!r} — all values were None "
            "or rejected by the value transform."
        )
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
    """Embed an indexed RGBA palette into an integer GeoTIFF band."""
    max_key = max(palette.keys())
    cmap = {
        i: ((*_hex_to_rgb(palette[i]), 255) if i in palette else TRANSPARENT)
        for i in range(max_key + 1)
    }
    with rasterio.open(raster_path, "r+") as dst:
        dst.write_colormap(1, cmap)
    logger.info("Embedded palette in %s", raster_path.name)


def _write_rgb(
    source_path: Path,
    output_path: Path,
    nodata: int | float,
    map_value: Callable[[np.ndarray], np.ndarray],
) -> None:
    """Render a single-band raster as a 3-band RGB GeoTIFF."""
    with rasterio.open(source_path) as src:
        data = src.read(1)
        profile = src.profile.copy()

    mask = data != nodata
    rgb_pixels = map_value(data[mask])
    rgb = np.zeros((3, *data.shape), dtype=np.uint8)
    for i in range(3):
        rgb[i][mask] = rgb_pixels[:, i]

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


def _interp_mapper(stops: list[tuple[int, str]]) -> Callable[[np.ndarray], np.ndarray]:
    values = np.array([s[0] for s in stops], dtype=np.float32)
    colors = np.array([_hex_to_rgb(s[1]) for s in stops], dtype=np.uint8)

    def _map(flat: np.ndarray) -> np.ndarray:
        out = np.zeros((flat.size, 3), dtype=np.uint8)
        for i in range(3):
            out[:, i] = np.clip(np.interp(flat, values, colors[:, i]), 0, 255)
        return out

    return _map


def _palette_mapper(palette: dict[int, str]) -> Callable[[np.ndarray], np.ndarray]:
    max_key = max(palette.keys())
    lut = np.zeros((max_key + 1, 3), dtype=np.uint8)
    for k, hex_color in palette.items():
        lut[k] = _hex_to_rgb(hex_color)

    def _map(flat: np.ndarray) -> np.ndarray:
        clipped = np.clip(flat.astype(np.int64), 0, max_key)
        return lut[clipped]

    return _map


def _process_calque(name: str, config: CalqueConfig, ref: dict, union) -> Path:
    if config.tif_path:
        path = RASTERS_DIR / config.tif_path
        if not path.exists():
            raise ValueError(f"Raster not found: {path}")
        if config.palette:
            _embed_palette(path, config.palette)
        return path

    if not config.model_name or not config.field:
        raise ValueError(f"CalqueConfig for {name!r} must set model_name and field.")
    model_class = apps.get_model("iarbre_data", config.model_name)
    qs = model_class.objects.filter(geometry__intersects=union)
    array = _rasterize_field(
        qs, config.field, config.dtype, config.nodata, ref, config.value_transform
    )
    path = RASTERS_DIR / f"{name}.tif"
    _write_geotiff(array, path, config.dtype, config.nodata, ref)

    if config.palette:
        _embed_palette(path, config.palette)
        if config.export_colors:
            _write_rgb(
                path,
                RASTERS_DIR / f"{name}_colors.tif",
                config.nodata,
                _palette_mapper(config.palette),
            )
    elif config.stops and config.export_colors:
        _write_rgb(
            path,
            RASTERS_DIR / f"{name}_colors.tif",
            config.nodata,
            _interp_mapper(config.stops),
        )

    return path


class Command(BaseCommand):
    help = "Rasterize calques with platform colors."

    def add_arguments(self, parser):
        parser.add_argument(
            "--model",
            choices=list(CALQUE_REGISTRY.keys()),
            default=None,
            help="Process a single calque. If omitted, processes all.",
        )

    def handle(self, *args, **options):
        names = [options["model"]] if options["model"] else list(CALQUE_REGISTRY.keys())
        ref = _reference_grid()
        union = _metro_geometry()

        for name in names:
            start = time.monotonic()
            path = _process_calque(name, CALQUE_REGISTRY[name], ref, union)
            elapsed = time.monotonic() - start
            self.stdout.write(
                self.style.SUCCESS(f"  {name} -> {path} in {elapsed:.1f}s")
            )
