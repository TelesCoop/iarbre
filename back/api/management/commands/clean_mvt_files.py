from django.core.management import BaseCommand
from iarbre_data.models import MVTTile


class Command(BaseCommand):
    help = "Clean all existing tiles"

    def add_arguments(self, parser):
        parser.add_argument(
            "--geolevel",
            type=str,
            required=True,
            help="What geolevel mvt to delete",
        )
        parser.add_argument(
            "--datatype",
            type=str,
            required=True,
            help="What datatype mvt to delete.",
        )

    def handle(self, *args, **options):
        geolevel = options["geolevel"]
        datatype = options["datatype"]
        print("Deleting existing MVTTile")
        print(
            MVTTile.objects.filter(
                geolevel=geolevel.lower(), datatype=datatype
            ).delete()
        )
