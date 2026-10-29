import os

import numpy as np
import rasterio
import shapely
from django.conf import settings
from django.contrib.gis.db.models.functions import AsWKB, Transform
from django.contrib.gis.geos import Polygon as GEOSPolygon
from django.core.management import BaseCommand
from django.db.models import F
from rasterio.features import rasterize
from rasterio.windows import Window
from tqdm import tqdm

from iarbre_data.models import Vegestrate
from iarbre_data.utils.database import log_progress

RASTER_PATH = os.path.join(
    settings.MEDIA_ROOT, "rasters/WMS", "vegestrate_02_2023_elevation.tif"
)
# ponytail: 1024 = 4x the 256px block size, keeps peak RAM ~2.5GB instead of ~5GB
STRIP_HEIGHT = 1024
BATCH_SIZE = 20000


def compute_sums_and_counts(raster_path: str, strip_height: int) -> tuple[dict, dict]:
    sums: dict[int, float] = {}
    counts: dict[int, int] = {}

    with rasterio.open(raster_path) as src:
        nodata = src.nodata
        width, height = src.width, src.height
        raster_srid = src.crs.to_epsg()

        for row_start in tqdm(range(0, height, strip_height), desc="Strips"):
            row_end = min(row_start + strip_height, height)
            strip_h = row_end - row_start
            window = Window(0, row_start, width, strip_h)
            strip_transform = src.window_transform(window)

            left, top = strip_transform * (0, 0)
            right, bottom = strip_transform * (width, strip_h)
            bbox = GEOSPolygon.from_bbox((left, bottom, right, top))
            bbox.srid = raster_srid

            qs = (
                Vegestrate.objects.filter(geometry__intersects=bbox)
                .annotate(geom_raster=AsWKB(Transform(F("geometry"), raster_srid)))
                .values_list("id", "geom_raster")
            )
            rows = [(pk, g) for pk, g in qs if g]
            if not rows:
                continue
            pks = [pk for pk, _ in rows]
            geoms = shapely.from_wkb([bytes(g) for _, g in rows])

            # ponytail: burn dense 1..N indices, not pks -- int32 would overflow BigAutoField
            ids = rasterize(
                zip(geoms, range(1, len(pks) + 1)),
                out_shape=(strip_h, width),
                transform=strip_transform,
                fill=0,
                dtype=np.int32,
            )
            elevation = src.read(1, window=window)

            valid = ids != 0
            if nodata is not None:
                valid &= elevation != nodata
            flat_ids = ids[valid]
            if flat_ids.size == 0:
                continue
            flat_elev = elevation[valid]

            nbins = len(pks) + 1
            group_sums = np.bincount(flat_ids, weights=flat_elev, minlength=nbins)
            group_counts = np.bincount(flat_ids, minlength=nbins)

            for idx in np.nonzero(group_counts[1:])[0] + 1:
                pk = pks[idx - 1]
                sums[pk] = sums.get(pk, 0.0) + group_sums[idx]
                counts[pk] = counts.get(pk, 0) + int(group_counts[idx])

    return sums, counts


def save_mean_heights(sums: dict, counts: dict) -> None:
    Vegestrate.objects.bulk_update(
        [
            Vegestrate(id=pk, mean_height=round(total / counts[pk], 2))
            for pk, total in sums.items()
        ],
        ["mean_height"],
        batch_size=BATCH_SIZE,
    )


class Command(BaseCommand):
    help = "Populate Vegestrate.mean_height from the vegestrate elevation raster."

    def add_arguments(self, parser):
        parser.add_argument("--strip-height", type=int, default=STRIP_HEIGHT)

    def handle(self, *args, **options):
        log_progress("Computing mean height per Vegestrate polygon from raster")
        sums, counts = compute_sums_and_counts(RASTER_PATH, options["strip_height"])
        total = Vegestrate.objects.count()
        uncovered = total - len(sums)
        log_progress(f"Saving mean_height for {len(sums)} polygons")
        save_mean_heights(sums, counts)
        if uncovered:
            log_progress(
                f"{uncovered} / {total} polygons ({100 * uncovered / total:.1f}%) had "
                "no raster coverage and keep mean_height=NULL"
            )
        log_progress("Done", star=True)
