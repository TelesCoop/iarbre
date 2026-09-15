import json
from collections import defaultdict

from django.core.management import BaseCommand
from tqdm import tqdm

from iarbre_data.models import City, Iris


def _compute_meta_factors_avg(tiles_qs):
    totals = defaultdict(float)
    count = 0
    for raw in (
        tiles_qs.exclude(meta_factors__isnull=True)
        .values_list("meta_factors", flat=True)
        .iterator(chunk_size=10_000)
    ):
        mf = json.loads(raw) if isinstance(raw, str) else raw
        for key, val in mf.get("meta_factors", {}).items():
            totals[key] += float(val)
        count += 1
    if count == 0:
        return None
    return {k: round(v / count, 4) for k, v in totals.items()}


class Command(BaseCommand):
    help = "Compute meta_factors_avg for City and Iris based on tile meta_factors"

    def handle(self, *args, **options):
        cities = list(City.objects.all())
        self.stdout.write(
            self.style.SUCCESS(
                f"Computing meta_factors_avg for {len(cities)} cities..."
            )
        )
        for city in tqdm(cities, desc="Processing cities"):
            avg = _compute_meta_factors_avg(city.tiles.all())
            city.meta_factors_avg = avg
            city.save(update_fields=["meta_factors_avg"])

        iris_list = list(Iris.objects.all())
        self.stdout.write(
            self.style.SUCCESS(
                f"Computing meta_factors_avg for {len(iris_list)} IRIS..."
            )
        )
        for iris in tqdm(iris_list, desc="Processing IRIS"):
            avg = _compute_meta_factors_avg(iris.tiles.all())
            iris.meta_factors_avg = avg
            iris.save(update_fields=["meta_factors_avg"])

        self.stdout.write(self.style.SUCCESS("Done computing meta_factors_avg."))
