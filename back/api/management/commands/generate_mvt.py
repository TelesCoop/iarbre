"""Generate MVT tiles for geographic model.

This script provides a Django management command to generate MVT (Mapbox Vector Tiles)
for specified geographic models. It supports multi-threading for improved performance
and allows for the deletion of existing tiles before generating new ones.
"""

from typing import Tuple, Type

from django.core.management import BaseCommand
from django.db.models import QuerySet, Model

from api.constants import DEFAULT_ZOOM_LEVELS, GeoLevel, DataType
from api.utils.mvt_generator import MVTGenerator
from iarbre_data.models import (
    Tile,
    Lcz,
    Vulnerability,
    Cadastre,
    MVTTile,
    BiosphereFunctionalIntegrity,
)


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
        queryset: QuerySet,
        zoom_levels: Tuple[int, int] = DEFAULT_ZOOM_LEVELS,
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
            datatype=model.datatype,
            geolevel=model.geolevel,
            number_of_thread=number_of_thread,
        )

        mvt_generator.generate_tiles()
        self.stdout.write(self.style.SUCCESS("MVT tiles generated successfully!"))

    def handle(self, *args, **options):
        """Handle the command."""
        number_of_thread = options["number_of_thread"]
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
        elif (
            geolevel == GeoLevel.BIOSPHERE_INTEGRITY.value
            and datatype == DataType.BIOSPHERE_INTEGRITY.value
        ):
            mdl = BiosphereFunctionalIntegrity
        else:
            supported_levels = [
                GeoLevel.TILE.value,
                GeoLevel.LCZ.value,
                GeoLevel.CADASTRE.value,
                GeoLevel.BIOSPHERE_INTEGRITY.value,
            ]
            raise ValueError(
                f"Unsupported geolevel: {geolevel}. Currently supported: {', '.join(supported_levels)}"
            )

        if options["keep"] is False:
            print(f"Deleting existing MVTTile for model : {mdl._meta.model_name}.")
            print(
                MVTTile.objects.filter(
                    geolevel=geolevel, datatype=mdl.datatype
                ).delete()
            )
        # Generate new tiles
        self.generate_tiles_for_model(
            model=mdl,
            queryset=mdl.objects.all(),
            zoom_levels=zoom_levels,
            number_of_thread=number_of_thread,
        )
