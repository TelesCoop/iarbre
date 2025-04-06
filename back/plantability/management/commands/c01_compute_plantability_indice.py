"""Compute and save indice data for the selected cities."""
import pandas as pd
import geopandas as gpd
import shapely
from django.db import transaction
from django.core.management import BaseCommand
from django.contrib.gis.geos import GEOSGeometry

from iarbre_data.data_config import FACTORS, PLANTABILITY_THRESHOLDS
from iarbre_data.models import Tile, TileFactor
from iarbre_data.utils.database import (
    load_geodataframe_from_db,
    select_city,
    log_progress,
)
from tqdm import tqdm

SAMPLE_LIMIT = 2_500_000


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
    factors = pd.Series(FACTORS)
    factors.name = "factor_coeff"
    df = df.join(factors, on="factor")
    df["value"] = df["value"] * df["factor_coeff"]
    df = df.groupby("tile_id", as_index=False)["value"].sum()

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


def score_thresholding(value):
    """Function to determine the plantabilty normalize index based on thresholds."""
    for i, threshold in enumerate(PLANTABILITY_THRESHOLDS):
        if value < threshold:
            return i * 2
    return 10


def compute_robust_normalized_indice() -> None:
    """Robust normalization of the data and then thresholding to produce a normalized indice between 0 and 10."""
    print("Computing Q1, Q3 and median")
    total_count = Tile.objects.all().count()
    if total_count > SAMPLE_LIMIT:
        sampled_ids = list(
            Tile.objects.order_by("?").values_list("id", flat=True)[:SAMPLE_LIMIT]
        )
        qs = (
            Tile.objects.filter(id__in=sampled_ids)
            .order_by("plantability_indice")
            .values_list("plantability_indice", flat=True)
        )
        del sampled_ids
    else:
        qs = Tile.objects.order_by("plantability_indice").values_list(
            "plantability_indice", flat=True
        )
    count = qs.count()
    q1_index = int(round(0.25 * count))
    q3_index = int(round(0.75 * count))
    median_index = int(round(0.5 * count))
    q1_value = qs[q1_index]
    median_value = qs[median_index]
    q3_value = qs[q3_index]
    iqr = q3_value - q1_value
    print(f"Q1: {q1_value}, Q3: {q3_value}, Median: {median_value}, IQR: {iqr}")
    del qs  # Free memory

    # Fetch in batches to avoid OOM issues
    batch_size = int(1e4)
    last_processed_id = 0
    qs = Tile.objects.all()
    total_batches = (len(qs) + batch_size - 1) // batch_size
    all_fields = [field.name for field in Tile._meta.get_fields() if field.concrete]
    with tqdm(total=total_batches, desc="Processing Batches") as pbar:
        while True:
            qs_batch = qs.filter(id__gt=last_processed_id).order_by("id")[:batch_size]

            if len(qs_batch) == 0:
                break
            df = gpd.GeoDataFrame(
                [
                    dict(
                        **{field: getattr(data, field) for field in all_fields},
                    )
                    for data in qs_batch
                ]
            )
            df.geometry = df["geometry"].apply(lambda el: shapely.wkt.loads(el.wkt))
            df = df.set_geometry("geometry")
            df["robust_scaling"] = (df.plantability_indice - median_value) / iqr
            df["plantability_normalized_indice"] = df["robust_scaling"].apply(
                score_thresholding
            )
            with transaction.atomic():
                Tile.objects.bulk_update(
                    [
                        Tile(
                            id=row.id,
                            plantability_normalized_indice=row.plantability_normalized_indice,
                        )
                        for row in df.itertuples()
                    ],
                    ["plantability_normalized_indice"],
                    batch_size=10000,
                )
            last_processed_id = df.iloc[-1].id
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
            log_progress(f"{city.name} ({idx+1} on {nb_city} city).")
            tiles_queryset = Tile.objects.filter(
                geometry__intersects=GEOSGeometry(city.geometry.wkt)
            )
            tiles_df = load_geodataframe_from_db(tiles_queryset, ["id"])
            compute_indice(tiles_df["id"])
        log_progress("Computing normalized indice.")
        compute_robust_normalized_indice()
