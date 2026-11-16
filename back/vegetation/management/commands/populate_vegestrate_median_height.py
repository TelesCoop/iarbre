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


def compute_median_heights(raster_path: str, strip_height: int) -> dict[int, float]:
    medians: dict[int, float] = {}
    pending: dict[int, list[np.ndarray]] = {}

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
            flat_elev = elevation[valid]
            order = np.argsort(flat_ids, kind="stable")
            flat_ids, flat_elev = flat_ids[order], flat_elev[order]
            idx, first = np.unique(flat_ids, return_index=True)
            for i, values in zip(idx, np.split(flat_elev, first[1:])):
                pending.setdefault(pks[i - 1], []).append(values)

            done = shapely.bounds(geoms)[:, 1] >= bottom
            for pk in np.asarray(pks)[done]:
                if pk in pending:
                    medians[pk] = float(np.median(np.concatenate(pending.pop(pk))))

    for pk, chunks in pending.items():
        medians[pk] = float(np.median(np.concatenate(chunks)))
    return medians


def save_median_heights(medians: dict) -> None:
    Vegestrate.objects.bulk_update(
        [Vegestrate(id=pk, median_height=round(m, 2)) for pk, m in medians.items()],
        ["median_height"],
        batch_size=BATCH_SIZE,
    )


class Command(BaseCommand):
    help = "Populate Vegestrate.median_height from the vegestrate elevation raster."

    def add_arguments(self, parser):
        parser.add_argument("--strip-height", type=int, default=STRIP_HEIGHT)

    def handle(self, *args, **options):
        log_progress("Computing median height per Vegestrate polygon from raster")
        medians = compute_median_heights(RASTER_PATH, options["strip_height"])
        total = Vegestrate.objects.count()
        uncovered = total - len(medians)
        log_progress(f"Saving median_height for {len(medians)} polygons")
        save_median_heights(medians)
        if uncovered:
            log_progress(
                f"{uncovered} / {total} polygons ({100 * uncovered / total:.1f}%) had "
                "no raster coverage and keep median_height=NULL"
            )
        log_progress("Done", star=True)
