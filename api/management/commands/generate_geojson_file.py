from django.core.management.base import BaseCommand

from api.map import generate_geojson_file
from iarbre_data.models import Tile


class Command(BaseCommand):
    help = "Generate a GeoJSON file from Tile model instances"

    def handle(self, *args, **kwargs):
        generate_geojson_file(Tile.objects.all(), Tile)
