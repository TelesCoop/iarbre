import math

from django.contrib.gis.db.models.functions import Area, Intersection
from django.core.management import BaseCommand
from django.db.models import Sum
from tqdm import tqdm

from iarbre_data.models import (
    BiosphereFunctionalIntegrity,
    BiosphereFunctionalIntegrityLandCover,
)
from iarbre_data.settings import SRID_DB
from iarbre_data.utils.database import log_progress

RADIUS_M = 500
CIRCLE_AREA = math.pi * RADIUS_M**2
BATCH_SIZE = 1000


def compute_indice() -> None:
    qs = BiosphereFunctionalIntegrityLandCover.objects.only("id", "geometry")
    to_create = []

    for lc in tqdm(qs.iterator(chunk_size=BATCH_SIZE), total=qs.count()):
        buffer = lc.geometry.centroid.buffer(RADIUS_M)
        buffer.srid = SRID_DB

        binary_area = (
            BiosphereFunctionalIntegrityLandCover.objects.filter(
                binary=True, geometry__intersects=buffer
            ).aggregate(total=Sum(Area(Intersection("geometry", buffer))))["total"]
            or 0.0
        )

        indice = min(100, round(float(binary_area) / CIRCLE_AREA * 100))
        to_create.append(
            BiosphereFunctionalIntegrity(geometry=lc.geometry, indice=indice)
        )

        if len(to_create) >= BATCH_SIZE:
            BiosphereFunctionalIntegrity.objects.bulk_create(to_create)
            to_create.clear()

    if to_create:
        BiosphereFunctionalIntegrity.objects.bulk_create(to_create)


class Command(BaseCommand):
    help = "Compute BiosphereFunctionalIntegrity indice from LandCover data."

    def handle(self, *args, **options):
        log_progress("Delete existing data")
        BiosphereFunctionalIntegrity.objects.all().delete()
        log_progress("Compute indice")
        compute_indice()
