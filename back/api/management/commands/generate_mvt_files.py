import os

from django.core.management import BaseCommand

from api.utils.mvt_generator import MVTGenerator
from iarbre_data import settings
from iarbre_data.models import Tile, MVTTile


class Command(BaseCommand):
    help = "Generate MVT tiles for geographic model"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number_of_thread",
            type=int,
            default=1,
            help="Number of threads to use for generating tiles",
        )

        parser.add_argument(
            "--keep",
            action="store_true",
            help="Keep already existing tiles, do not delete them.",
        )

    def generate_tiles_for_model(
        self, model, queryset, output_dir, zoom_levels=(10, 20), number_of_thread=1
    ):
        # Generate MVT tiles
        mvt_generator = MVTGenerator(
            queryset=queryset,
            zoom_levels=zoom_levels,
            layer_name=model.type,
            output_dir=output_dir,
            number_of_thread=number_of_thread,
        )

        mvt_generator.generate_tiles()
        self.stdout.write(self.style.SUCCESS("MVT tiles generated successfully!"))

    def handle(self, *args, **options):
        number_of_thread = options["number_of_thread"]
        # Generate MVT tiles for Tile model
        if options["keep"] is False:
            print("Deleting existing MVTTile")
            MVTTile.objects.all().delete()
        self.generate_tiles_for_model(
            Tile,
            Tile.objects.all(),
            os.path.join(settings.BASE_DIR, "mvt_files", "tile"),
            (8, 16),
            number_of_thread,
        )
