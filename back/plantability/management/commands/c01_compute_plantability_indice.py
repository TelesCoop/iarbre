"""Compute and save indice data for the selected cities."""
import pandas as pd
from django.db import transaction
from django.core.management import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from django.db.models import Min, Max
from django.db.models import F


from iarbre_data.data_config import FACTORS
from iarbre_data.models import Tile, TileFactor
from iarbre_data.management.commands.utils import (
    load_geodataframe_from_db,
    select_city,
)
from tqdm import tqdm


def compute_indice(tiles_id) -> None:
    """
    Compute the indice for a list of tiles. The indice is computed as the weighted sum of the factors (land occupancy proportion) for each tile.

    Args:
        tiles_id (list[int]): List of tile ids to compute the indice for.

    Returns:
        None
    """
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
    with transaction.atomic():
        Tile.objects.bulk_update(
            [
                Tile(
                    id=row.tile_id,
                    plantability_indice=row.value,
                )
                for row in df.itertuples()
            ],
            ["plantability_indice"],
            batch_size=10000,
        )


def compute_normalized_indice() -> None:
    """Normalized indice is a score between 0 and 1."""

    # Calculate the min and max directly in the database
    min_indice = Tile.objects.aggregate(Min("plantability_indice"))[
        "plantability_indice__min"
    ]
    max_indice = Tile.objects.aggregate(Max("plantability_indice"))[
        "plantability_indice__max"
    ]

    # Fetch in batches to avoid OOM issues
    batch_size = int(1e6)
    last_processed_id = 0
    qs = Tile.objects.all()
    print(f"Total tiles: {len(qs)} with a  batch size of {batch_size}.")
    total_batches = (len(qs) + batch_size - 1) // batch_size
    with tqdm(total=total_batches, desc="Processing Batches") as pbar:
        while True:
            tiles_batch = list(
                qs.filter(id__gt=last_processed_id)
                .order_by("id")
                .values_list("id", flat=True)[:batch_size]
            )
            if not tiles_batch:
                break
            with transaction.atomic():
                Tile.objects.filter(id__in=tiles_batch).update(
                    plantability_normalized_indice=(
                        F("plantability_indice") - min_indice
                    )
                    / (max_indice - min_indice)
                )
            last_processed_id = tiles_batch[-1]
            pbar.update(1)


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
        """Compute and save indice data for the selected cities."""
        insee_code_city = options["insee_code_city"]

        selected_city = select_city(insee_code_city)
        nb_city = len(selected_city)
        for idx, city in enumerate(selected_city.itertuples()):
            print(f"{city.name} ({idx+1} on {nb_city} city).")
            tiles_queryset = Tile.objects.filter(
                geometry__intersects=GEOSGeometry(city.geometry.wkt)
            )
            tiles_df = load_geodataframe_from_db(tiles_queryset, ["id"])
            compute_indice(tiles_df["id"])
        print("Computing normalized indice.")
        compute_normalized_indice()
