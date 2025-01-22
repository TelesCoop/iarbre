from django.core.management import BaseCommand
from iarbre_data.models import MVTTile


class Command(BaseCommand):
    help = "Clean all existing tiles"

    def handle(self, *args, **options):
        print("Deleting existing MVTTile")
        MVTTile.objects.all().delete()
