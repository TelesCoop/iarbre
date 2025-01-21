import pandas as pd
from django.core.management import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from django.db.models import Min, Max

from iarbre_data.data_config import FACTORS
from iarbre_data.models import Tile, TileFactor
from iarbre_data.management.commands.utils import load_geodataframe_from_db, select_city
from iarbre_data.management.commands.c02_init_grid import clean_outside


def compute_indice(tiles_id):
    df = pd.DataFrame(
        TileFactor.objects.filter(tile_id__in=tiles_id).values_list(
            "tile_id", "factor", "value"
        ),
        columns=["tile_id", "factor", "value"],
    )
    factors = pd.Series(FACTORS)  # make all factors positive
    factors.name = "factor_coeff"
    df = df.join(factors, on="factor")
    df["value"] = df["value"] * df["factor_coeff"]
    Tile.objects.bulk_update(
        [
            Tile(
                id=row.tile_id,
                indice=row.value,
            )
            for row in df.itertuples()
        ],
        ["indice"],
        batch_size=10000,
    )


def compute_normalized_indice() -> None:
    """Normalized indice is a score between 0 and 1."""
    tiles = load_geodataframe_from_db(Tile.objects.all(), ["id", "indice"])
    min_indice = tiles.indice.min()
    max_indice = tiles.indice.max()
    if min_indice is None or max_indice is None or min_indice == max_indice:
        print("Normalization not possible (no data or all values are the same).")
        return
    tiles["normalized_indice"] = (tiles["indice"] - min_indice) / (
        max_indice - min_indice
    )
    Tile.objects.bulk_update(
        [
            Tile(
                id=row.id,
                normalized_indice=row.normalized_indice,
            )
            for row in tiles.itertuples()
        ],
        ["normalized_indice"],
        batch_size=5000,
    )


class Command(BaseCommand):
    help = "Compute and save factors data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--insee_code_city",
            type=str,
            required=False,
            default=None,
            help="The INSEE code of the city or cities to process. If multiple cities, please separate with comma (e.g. --insee_code 69266,69382)",
        )

    def handle(self, *args, **options):
        insee_code_city = options["insee_code_city"]

        selected_city = select_city(insee_code_city)
        clean_outside(selected_city, int(1e4))
        nb_city = len(selected_city)
        for idx, city in enumerate(selected_city.itertuples()):
            print(f"{city.name} ({idx} on {nb_city} city).")
            tiles_queryset = Tile.objects.filter(
                geometry__intersects=GEOSGeometry(city.geometry.wkt)
            )
            tiles_df = load_geodataframe_from_db(tiles_queryset, ["id"])
            compute_indice(tiles_df["id"])
        print("Computing normalized indice.")
        compute_normalized_indice()
