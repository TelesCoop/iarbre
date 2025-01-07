import json
import os

from django.conf import settings
from django.core.management import BaseCommand
from django.db.models import Avg

from api.utils.mvt_generator import MVTGenerator
from iarbre_data.models import MVTTile, TileFactor, Tile


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
            "--clean",
            type=bool,
            default=False,
            help="Delete all existing tiles before generating new ones",
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

    def generate_mean_of_each_factor(self):
        mean_values = (
            TileFactor.objects.all().values("factor").annotate(mean_value=Avg("value"))
        )
        mean_values_by_factor = {
            mean_value["factor"]: mean_value["mean_value"] for mean_value in mean_values
        }

        file_path = os.path.join(settings.STATIC_ROOT, "mean_values_by_factor.json")
        # create directory if not exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as outfile:
            json.dump(mean_values_by_factor, outfile)

    def handle(self, *args, **options):
        number_of_thread = options["number_of_thread"]
        # Generate MVT tiles for Tile model
        if options["clean"]:
            print("Deleting existing MVTTile")
            MVTTile.objects.all().delete()
        self.generate_tiles_for_model(
            Tile,
            Tile.objects.all().prefetch_related("factors"),
            os.path.join(settings.BASE_DIR, "mvt_files", "tile"),
            (8, 16),
            number_of_thread,
        )
        self.generate_mean_of_each_factor()
