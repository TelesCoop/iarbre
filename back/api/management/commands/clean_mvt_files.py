from django.core.management import BaseCommand
from iarbre_data.models import MVTTile


class Command(BaseCommand):
    help = "Clean all existing tiles"

    def add_arguments(self, parser):
        parser.add_argument(
            "--model",
            type=str,
            required=True,
            help="What model mvt to delete",
        )
        parser.add_argument(
            "--datatype",
            type=str,
            required=True,
            help="What datatype mvt to delete.",
        )

    def handle(self, *args, **options):
        model = options["model"]
        layer = options["datatype"]
        print("Deleting existing MVTTile")
        print(MVTTile.objects.filter(geolevel=model.lower(), datatype=layer).delete())
