import os

from django.core.management import BaseCommand

from api.utils.mvt_generator import MVTGenerator
from iarbre_data import settings
from iarbre_data.models import Tile


class Command(BaseCommand):
    help = "Generate MVT tiles for geographic model"

    def generate_tiles_for_model(self, model, output_dir, zoom_levels=(10, 20)):
        # Generate MVT tiles
        mvt_generator = MVTGenerator(
            queryset=model.objects.all(),
            zoom_levels=zoom_levels,
            layer_name=model.type,
            output_dir=output_dir,
        )

        mvt_generator.generate_tiles()
        self.stdout.write(self.style.SUCCESS("MVT tiles generated successfully!"))

    def handle(self, *args, **options):
        # Generate MVT tiles for Tile model
        self.generate_tiles_for_model(
            Tile,
            os.path.join(settings.BASE_DIR, "mvt_files/tiles"),
            (12, 20),
        )
