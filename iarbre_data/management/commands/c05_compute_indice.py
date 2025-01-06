import pandas as pd
from django.core.management import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from django.db import transaction
from django.db.models import F, Value, Min, Max
from numba.np.arrayobj import normalize_indices

from iarbre_data.data_config import FACTORS
from iarbre_data.models import City, Tile, TileFactor
from iarbre_data.management.commands.utils import load_geodataframe_from_db


def compute_indice(tiles_id):
    df = pd.DataFrame(
        TileFactor.objects.filter(tile_id__in=tiles_id).values_list(
            "tile_id", "factor", "value"
        ),
        columns=["tile_id", "factor", "value"],
    )
    factors = pd.Series(FACTORS) + 5  # make all factors positive
    factors.name = "factor_coeff"
    df = df.join(factors, on="factor")
    df["value"] = df["value"] * df["factor_coeff"]
    grouped = (
        df.groupby("tile_id")
        .agg(weighted_sum=("value", "sum"), total_weight=("factor_coeff", "sum"))
        .reset_index()
    )
    # Compute normalized indice
    grouped["normalized_indice"] = grouped["weighted_sum"] / grouped["total_weight"]
    Tile.objects.bulk_update(
        [
            Tile(
                id=row.tile_id,
                indice=row.weighted_sum,
                normalized_indice=row.normalized_indice,
            )
            for row in grouped.itertuples()
        ],
        ["indice", "normalized_indice"],
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

        if insee_code_city is not None:  # Perform selection only for a city
            insee_code_city = insee_code_city.split(",")
            selected_city_qs = City.objects.filter(insee_code__in=insee_code_city)
            if not selected_city_qs.exists():
                raise ValueError(f"No city found with INSEE code {insee_code_city}")
            selected_city = load_geodataframe_from_db(
                selected_city_qs, ["name", "insee_code"]
            )
        else:
            selected_city = load_geodataframe_from_db(
                City.objects.all(), ["name", "insee_code"]
            )
        nb_city = len(selected_city)
        for city in selected_city.itertuples():
            print(f"Selected city: {city.name} (on {nb_city} city).")
            tiles_queryset = Tile.objects.filter(
                geometry__intersects=GEOSGeometry(city.geometry.wkt)
            )
            tiles_df = load_geodataframe_from_db(tiles_queryset, ["id"])
            compute_indice(tiles_df["id"])
