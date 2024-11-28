
from django.core.management.base import BaseCommand
from api.utils.mbtiles import MBTilesGenerator
from iarbre_data.models import Tile

class Command(BaseCommand):
    help = 'Generate MBTiles from spatial model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            help='Model to generate tiles from (app.ModelName)'
        )

    def handle(self, *args, **options):
        for (model, file_name) in [
            (Tile, "tiles.mbtiles"),
        ]:
            output_path = MBTilesGenerator.generate_mbtiles_from_model(Tile.objects.all(), filename=file_name)
            self.stdout.write(
                self.style.SUCCESS(f'MBTiles generated: {output_path}')
            )