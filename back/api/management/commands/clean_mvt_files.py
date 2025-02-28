from django.core.management import BaseCommand
from iarbre_data.models import MVTTile


class Command(BaseCommand):
    help = "Clean all existing tiles"

    def add_arguments(self, parser):
        parser.add_argument(
            "--model",
            type=str,
            required=True,
            help="What model to transform to MVT.",
        )

    def handle(self, *args, **options):
        model = options["model"]
        print("Deleting existing MVTTile")
        print(MVTTile.objects.filter(model_type=model.lower()).delete())
