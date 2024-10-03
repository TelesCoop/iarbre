from django.contrib.gis.utils import LayerMapping
from django.core.management import BaseCommand

from iarbre_data.models import City

mapping = {"geometry": "POLYGON", "name": "nom", "insee_code": "insee"}


class Command(BaseCommand):
    help = "Insert cities geojson file"

    def handle(self, *args, **options):
        lm = LayerMapping(City, "file_data/communes_gl.geojson", mapping)
        lm.save()
