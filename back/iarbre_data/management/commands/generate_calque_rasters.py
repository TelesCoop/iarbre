"""Rasterize Vulnerability and LCZ vector layers to GeoTIFF files.

Uses the plantability raster as a spatial reference (bounds, resolution, CRS)
to produce aligned outputs suitable for overlay in QGIS.

Usage:
    python manage.py generate_calque_rasters
    python manage.py generate_calque_rasters --calque vulnerability
    python manage.py generate_calque_rasters --calque lcz
"""

import logging
import time

import numpy as np
import rasterio
from rasterio.features import rasterize
from django.conf import settings
from django.contrib.gis.db.models import Union
from django.core.management import BaseCommand
from pathlib import Path

from iarbre_data.models import City, Vulnerability, Lcz
from iarbre_data.utils.database import load_geodataframe_from_db

logger = logging.getLogger(__name__)

RASTERS_DIR = Path(settings.MEDIA_ROOT) / "rasters"


def _reference_grid():
    """Read the plantability raster to get the reference grid parameters."""
    ref_path = RASTERS_DIR / "plantability.tif"
    with rasterio.open(ref_path) as src:
        return {
            "bounds": src.bounds,
            "res": src.res[0],
            "crs": src.crs,
            "transform": src.transform,
            "width": src.width,
            "height": src.height,
        }


def _all_cities_union():
    return City.objects.exclude(code="38250").aggregate(union=Union("geometry"))[
        "union"
    ]


def _rasterize_model(queryset, value_field, output_name, dtype, nodata, ref):
    """Rasterize a vector queryset into a GeoTIFF aligned to the reference grid."""
    gdf = load_geodataframe_from_db(queryset, ["id", value_field])
    if gdf.empty:
        raise ValueError(f"No data found for {output_name}")

    shapes = [
        (geom, val)
        for geom, val in zip(gdf.geometry, gdf[value_field])
        if val is not None
    ]

    logger.info("Rasterizing %s (%d features)", output_name, len(shapes))
    raster = rasterize(
        shapes,
        out_shape=(ref["height"], ref["width"]),
        transform=ref["transform"],
        fill=nodata,
        dtype=dtype,
    )

    output_path = RASTERS_DIR / f"{output_name}.tif"
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
        dst.write(raster, 1)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info("Generated %s (%.1f MB)", output_path, size_mb)
    return output_path


CALQUES = {
    "vulnerability": {
        "queryset_fn": lambda union: Vulnerability.objects.filter(
            geometry__intersects=union
        ),
        "value_field": "vulnerability_index_day",
        "dtype": np.float32,
        "nodata": -9999.0,
    },
    "lcz": {
        "queryset_fn": lambda union: Lcz.objects.filter(geometry__intersects=union),
        "value_field": "lcz_index",
        "dtype": np.int16,
        "nodata": -1,
    },
}


class Command(BaseCommand):
    help = "Rasterize vulnerability and LCZ layers to GeoTIFF."

    def add_arguments(self, parser):
        parser.add_argument(
            "--calque",
            choices=list(CALQUES.keys()),
            default=None,
            help="Rasterize a single calque. If omitted, rasterizes all.",
        )

    def handle(self, *args, **options):
        ref = _reference_grid()
        union = _all_cities_union()
        calques = [options["calque"]] if options["calque"] else list(CALQUES.keys())

        for name in calques:
            config = CALQUES[name]
            start = time.monotonic()
            qs = config["queryset_fn"](union)
            path = _rasterize_model(
                qs, config["value_field"], name, config["dtype"], config["nodata"], ref
            )
            elapsed = time.monotonic() - start
            self.stdout.write(
                self.style.SUCCESS(f"  {name} -> {path} in {elapsed:.1f}s")
            )
