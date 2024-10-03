import pandas as pd
from django.core.management import BaseCommand

from iarbre_data.data_config import FACTORS
from iarbre_data.models import Tile, TileFactor


def compute_indice():
    df = pd.DataFrame(
        TileFactor.objects.values_list("tile_id", "factor", "value"),
        columns=["tile_id", "factor", "value"],
    )
    factors = pd.Series(FACTORS)
    factors.name = "factor_coeff"
    df = df.join(factors, on="factor")
    df["value"] = df["value"] * df["factor_coeff"]
    df = df.groupby("tile_id")["value"].sum().reset_index()
    Tile.objects.bulk_update(
        [Tile(id=row.tile_id, indice=row.value) for row in df.itertuples()],
        ["indice"],
    )


class Command(BaseCommand):
    help = "Compute and save factors data."

    def handle(self, *args, **options):
        compute_indice()
