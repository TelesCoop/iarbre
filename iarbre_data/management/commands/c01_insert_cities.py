import logging

from django.contrib.gis.utils import LayerMapping
from django.core.management import BaseCommand
from django.db.models import Count

from iarbre_data.models import City

mapping = {"geometry": "POLYGON", "name": "nom", "insee_code": "insee"}


class Command(BaseCommand):
    help = "Insert cities geojson file"

    @staticmethod
    def _remove_duplicates():
        """Deletes duplicates in the City model based on geometry."""
        duplicates = (
            City.objects.values("geometry")
            .annotate(count=Count("id"))
            .filter(count__gt=1)
        )

        for duplicate in duplicates:
            geometry = duplicate["geometry"]
            duplicate_cities = City.objects.filter(geometry=geometry)
            # Keep the first and delete the rest
            ids_to_delete = duplicate_cities.values_list("id", flat=True)[1:]
            City.objects.filter(id__in=ids_to_delete).delete()
        print(f"Removed duplicates for {duplicates.count()} entries.")

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        lm = LayerMapping(City, "file_data/communes_gl.geojson", mapping)
        lm.save()
        logger.info("Data insertion complete.")
        print("Removing duplicates...")
        self._remove_duplicates()
        logger.info("Duplicate removal complete.")
