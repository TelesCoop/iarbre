import json
import os

import numpy as np
import rasterio
from django.contrib.gis.db.models import Union
from django.contrib.gis.db.models.functions import AsGeoJSON
from django.contrib.gis.geos import Polygon as GEOSPolygon
from django.core.management import BaseCommand
from rasterio.features import rasterize
from rasterio.transform import from_origin
from rasterio.windows import Window
from shapely.geometry import shape
from tqdm import tqdm

from iarbre_data.models import City, Vegestrate
from iarbre_data.settings import BASE_DIR
from iarbre_data.utils.database import log_progress

STRATE_VALUES = {
    "herbacee": 1,
    "arbustif": 2,
    "arborescent": 3,
}

STRIP_HEIGHT = 2000


class Command(BaseCommand):
    help = "Rasterize Vegestrate geometries into a single GeoTIFF."

    def add_arguments(self, parser):
        parser.add_argument(
            "--resolution", type=float, default=1.0, help="Pixel resolution in meters"
        )
        parser.add_argument("--output", type=str, default=None, help="Output file path")

    def handle(self, *args, **options):
        resolution = options["resolution"]
        output_path = options["output"] or os.path.join(
            str(BASE_DIR), "media", "rasters", "vegestrate", "vegestrate.tif"
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        log_progress("Computing extent from cities")
        all_cities_union = City.objects.exclude(code="38250").aggregate(
            union=Union("geometry")
        )["union"]
        minx, miny, maxx, maxy = all_cities_union.extent

        width = int((maxx - minx) / resolution)
        height = int((maxy - miny) / resolution)
        transform = from_origin(minx, maxy, resolution, resolution)

        log_progress(f"Raster size: {width}x{height} at {resolution}m resolution")

        with rasterio.open(
            output_path,
            "w",
            driver="GTiff",
            height=height,
            width=width,
            count=1,
            dtype=np.uint8,
            crs="EPSG:2154",
            transform=transform,
            compress="lzw",
        ) as dst:
            for row_start in tqdm(range(0, height, STRIP_HEIGHT), desc="Strips"):
                row_end = min(row_start + STRIP_HEIGHT, height)
                strip_h = row_end - row_start

                strip_maxy = maxy - row_start * resolution
                strip_miny = maxy - row_end * resolution
                strip_transform = from_origin(minx, strip_maxy, resolution, resolution)

                strip_bbox = GEOSPolygon.from_bbox((minx, strip_miny, maxx, strip_maxy))
                strip_bbox.srid = 2154

                qs = (
                    Vegestrate.objects.filter(geometry__intersects=strip_bbox)
                    .annotate(geom_json=AsGeoJSON("geometry"))
                    .values_list("geom_json", "strate")
                )

                shapes = sorted(
                    [
                        (shape(json.loads(geom_json)), STRATE_VALUES[strate])
                        for geom_json, strate in qs
                        if strate in STRATE_VALUES
                    ],
                    key=lambda x: x[1],
                )

                layer = rasterize(
                    shapes,
                    out_shape=(strip_h, width),
                    transform=strip_transform,
                    fill=0,
                    dtype=np.uint8,
                )
                dst.write(layer, 1, window=Window(0, row_start, width, strip_h))
