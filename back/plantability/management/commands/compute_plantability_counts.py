"""Compute plantability_counts for City and Iris models."""

from django.core.management import BaseCommand
from django.db.models import Count
from tqdm import tqdm

from iarbre_data.models import City, Iris, init_plantability_counts
from plantability.constants import PLANTABILITY_NORMALIZED


class Command(BaseCommand):
    help = "Compute plantability_counts for City and Iris based on plantability_normalized_indice values"

    def add_arguments(self, parser):
        parser.add_argument(
            "--city-code",
            type=str,
            help="Optional: Compute only for a specific city code",
        )

    def _compute_plantability_counts(self, instance):
        """Compute plantability counts for a City or Iris instance.

        Args:
            instance: City or Iris instance to compute counts for.
        """
        # Initialize counts with all possible values (as strings to match model)
        counts = init_plantability_counts()

        # Count tiles by plantability_normalized_indice
        tiles_counts = (
            instance.tiles.exclude(plantability_normalized_indice__isnull=True)
            .values("plantability_normalized_indice")
            .annotate(count=Count("id"))
        )

        for item in tiles_counts:
            indice_value = item["plantability_normalized_indice"]
            # Round to nearest value in PLANTABILITY_NORMALIZED to handle floating point
            normalized_value = min(
                PLANTABILITY_NORMALIZED, key=lambda x: abs(x - indice_value)
            )
            counts[str(normalized_value)] = item["count"]

        # Update the instance's plantability_counts
        instance.plantability_counts = counts
        instance.save(update_fields=["plantability_counts"])

    def handle(self, *args, **options):
        """Compute plantability_counts for all cities and IRIS."""
        cities = City.objects.all()

        # Compute counts for cities
        self.stdout.write(
            self.style.SUCCESS(
                f"Computing plantability_counts for {len(cities)} cities..."
            )
        )
        for city in tqdm(cities, desc="Processing cities"):
            self._compute_plantability_counts(city)

        # Compute counts for IRIS (filter by city if specified)
        iris_list = Iris.objects.all()

        self.stdout.write(
            self.style.SUCCESS(
                f"Computing plantability_counts for {len(iris_list)} IRIS..."
            )
        )
        for iris in tqdm(iris_list, desc="Processing IRIS"):
            self._compute_plantability_counts(iris)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully computed plantability_counts for all cities and IRIS!"
            )
        )
