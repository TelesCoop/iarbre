"""
Generate MVT tiles for geographic model.

This script provides a Django management command to generate MVT (Mapbox Vector Tiles)
for specified geographic models. It supports multi-threading for improved performance
and allows for the deletion of existing tiles before generating new ones.

Usage:
    python manage.py generate_mvt_tiles --number_of_thread=<num> --model=<model> [--keep]

Arguments:
    --number_of_thread: Number of threads to use for generating tiles (default: 1).
    --model: The model to transform to MVT (default: "Tile").
    --keep: Keep already existing tiles, do not delete them (default: False).

Models supported:
    - Tile
    - Lcz

Example:
    python manage.py generate_mvt_tiles --number_of_thread=4 --model=Tile --keep
"""

from typing import Tuple, Type

from django.core.management import BaseCommand

from django.db.models import QuerySet, Model

from api.utils.mvt_generator import MVTGenerator

from iarbre_data.models import Tile, Lcz, MVTTile


class Command(BaseCommand):
    help = "Generate MVT file for a specif model."

    def add_arguments(self, parser):
        parser.add_argument(
            "--number_of_thread",
            type=int,
            default=1,
            help="Number of threads to use for generating tiles",
        )
        parser.add_argument(
            "--model",
            type=str,
            required=True,
            help="What model to transform to MVT.",
        )
        parser.add_argument(
            "--keep",
            action="store_true",
            help="Keep already existing tiles, do not delete them.",
        )

    def generate_tiles_for_model(
        self,
        model: Type[Model],
        queryset: QuerySet,
        zoom_levels: Tuple[int, int] = (8, 20),
        number_of_thread: int = 1,
    ) -> None:
        """
        Generate MVT tiles for a geographic model.

        This method generates MVT (Mapbox Vector Tiles) for a specified geographic model
        based on the provided queryset and zoom levels. It utilizes multiple threads
        to enhance performance.

        Args:
            model (Type[Model]): The model class to generate MVT tiles for.
            queryset (QuerySet): The queryset of the model instances to process.
            zoom_levels (Tuple[int, int]): A tuple specifying the range of zoom levels
                                           to generate tiles for (inclusive).
            number_of_thread (int): The number of threads to use for generating tiles.

        Returns:
            None
        """
        mvt_generator = MVTGenerator(
            queryset=queryset,
            zoom_levels=zoom_levels,
            layer_name=model.type,
            number_of_thread=number_of_thread,
        )

        mvt_generator.generate_tiles()
        self.stdout.write(self.style.SUCCESS("MVT tiles generated successfully!"))

    def handle(self, *args, **options):
        """Handle the command."""
        number_of_thread = options["number_of_thread"]
        model = options["model"]
        if model == "Tile":
            mdl = Tile
        elif model == "Lcz":
            mdl = Lcz
        else:
            raise ValueError(
                f"Unsupported model: {model}. Should be either 'Tile' or 'Lcz'."
            )

        if options["keep"] is False:
            print(f"Deleting existing MVTTile for model : {model}.")
            print(MVTTile.objects.filter(model_type=model.lower()).delete())
        # Generate new tiles
        self.generate_tiles_for_model(
            mdl,
            mdl.objects.all(),
            (10, 20),
            number_of_thread,
        )
