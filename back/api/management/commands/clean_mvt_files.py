from django.core.management import BaseCommand
from iarbre_data.models import MVTTile


class Command(BaseCommand):
    help = "Clean all existing tiles"

    def add_arguments(self, parser):
        parser.add_argument(
            "--geolevel",
            type=str,
            help="What geolevel MVT to delete (optional). If not provided delete all.",
        )
        parser.add_argument(
            "--datatype",
            type=str,
            help="What datatype MVT to delete (optional). If not provided delete all.",
        )

    def handle(self, *args, **options):
        geolevel = options.get("geolevel")
        datatype = options.get("datatype")

        if geolevel and datatype:
            deleted_count, _ = MVTTile.objects.filter(
                geolevel=geolevel.lower(), datatype=datatype
            ).delete()
        else:
            deleted_count, _ = MVTTile.objects.all().delete()

        print(f"Deleted {deleted_count} MVTTile objects.")
