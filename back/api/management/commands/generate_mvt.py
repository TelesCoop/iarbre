"""Generate MVT tiles for geographic model.

This script provides a Django management command to generate MVT (Mapbox Vector Tiles)
for specified geographic models. It supports multi-threading for improved performance
and allows for the deletion of existing tiles before generating new ones.
"""

from typing import Tuple, Type

from django.core.management import BaseCommand
from django.db.models import Model

from api.constants import DEFAULT_ZOOM_LEVELS, GeoLevel, DataType
from api.utils.mvt_generator import MVTGenerator
from iarbre_data.models import Tile, Lcz, Vulnerability, Cadastre, MVTTile


class Command(BaseCommand):
    help = "Generate MVT file for a specif model."

    def add_arguments(self, parser):
        parser.add_argument(
            "--number_of_workers",
            type=int,
            default=1,
            help="Number of workers to use for generating tiles",
        )
        parser.add_argument(
            "--number_of_threads_by_worker",
            type=int,
            default=1,
            help="Number of threads by worker to use for generating tiles",
        )
        parser.add_argument(
            "--geolevel",
            type=str,
            required=True,
            choices=[choice for choice, _ in GeoLevel.choices],
            help=f"What geolevel to transform to MVT. Choices: {', '.join([choice for choice, _ in GeoLevel.choices])}",
        )
        parser.add_argument(
            "--datatype",
            type=str,
            required=True,
            choices=[choice for choice, _ in DataType.choices],
            help=f"What datatype to transform to MVT. Choices: {', '.join([choice for choice, _ in DataType.choices])}",
        )
        parser.add_argument(
            "--keep",
            action="store_true",
            help="Keep already existing tiles, do not delete them.",
        )
        parser.add_argument(
            "--zoom_levels",
            type=tuple,
            default=DEFAULT_ZOOM_LEVELS,
            help="Zoom levels to generate MVTs.",
        )

    def generate_tiles_for_model(
        self,
        model: Type[Model],
        zoom_levels: Tuple[int, int] = DEFAULT_ZOOM_LEVELS,
        number_of_threads_by_worker: int = 1,
        number_of_workers: int = 1,
    ) -> None:
        """
        Generate MVT tiles for a geographic model.

        This method generates MVT (Mapbox Vector Tiles) for a specified geographic model
        based on the provided model and zoom levels. It utilizes multiple threads
        to enhance performance.

        Args:
            model (Type[Model]): The model class to generate MVT tiles for.
            zoom_levels (Tuple[int, int]): A tuple specifying the range of zoom levels
                                           to generate tiles for (inclusive).
            number_of_workers (int): The number of workers to use for generating tiles.

        Returns:
            None
        """
        mvt_generator = MVTGenerator(
            mdl=model,
            zoom_levels=zoom_levels,
            number_of_workers=number_of_workers,
            number_of_threads_by_worker=number_of_threads_by_worker,
        )

        mvt_generator.generate_tiles()
        self.stdout.write(self.style.SUCCESS("MVT tiles generated successfully!"))

    def handle(self, *args, **options):
        """Handle the command."""
        number_of_workers = options["number_of_workers"]
        number_of_threads_by_worker = options["number_of_threads_by_worker"]
        geolevel = options["geolevel"]
        datatype = options["datatype"]
        zoom_levels = options["zoom_levels"]
        if geolevel == GeoLevel.TILE.value:
            mdl = Tile
        elif geolevel == GeoLevel.LCZ.value and datatype == DataType.LCZ.value:
            mdl = Lcz
        elif (
            geolevel == GeoLevel.LCZ.value and datatype == DataType.VULNERABILITY.value
        ):
            mdl = Vulnerability
        elif (
            geolevel == GeoLevel.CADASTRE.value and datatype == DataType.CADASTRE.value
        ):
            mdl = Cadastre
        else:
            supported_levels = [
                GeoLevel.TILE.value,
                GeoLevel.LCZ.value,
                GeoLevel.CADASTRE.value,
            ]
            raise ValueError(
                f"Unsupported geolevel: {geolevel}. Currently supported: {', '.join(supported_levels)}"
            )

        if options["keep"] is False:
            print(f"Deleting existing MVTTile for model : {mdl._meta.model_name}.")
            print(
                MVTTile.objects.filter(
                    geolevel=mdl.geolevel,
                    datatype=mdl.datatype,
                    zoom_level__gte=zoom_levels[0],
                    zoom_level__lte=zoom_levels[1],
                ).delete()
            )
        # Generate new tiles
        self.generate_tiles_for_model(
            model=mdl,
            zoom_levels=zoom_levels,
            number_of_workers=number_of_workers,
            number_of_threads_by_worker=number_of_threads_by_worker,
        )
