import time

from django.core.management import BaseCommand
from tqdm import tqdm

from iarbre_data.data_config import FACTORS
from iarbre_data.management.commands.utils import load_geodataframe_from_db
from iarbre_data.models import Data, Tile, TileFactor, City


TILE_BATCH_SIZE = 10_000


def _compute_for_factor_partial_tiles(factor_name, factor_df, tiles_df, std_area):
    # we intersect with data for this factor
    df = tiles_df.clip(factor_df)
    df["value"] = df.geometry.area / std_area
    tile_factors = [
        TileFactor(tile_id=row.id, factor=factor_name, value=row.value)
        for row in df.itertuples()
    ]
    TileFactor.objects.bulk_create(tile_factors)


def compute_for_factor(factor_name, tiles_df):
    std_area = Tile.objects.first().geometry.area
    # remove former factors
    TileFactor.objects.filter(factor=factor_name).delete()

    qs = Data.objects.filter(factor=factor_name)
    if not qs.exists():
        return
    factor_df = load_geodataframe_from_db(qs, [])

    # compute by batch of 10k tiles
    n_batches = len(tiles_df) // TILE_BATCH_SIZE + 1
    for batch in tqdm(
        range(0, len(tiles_df), TILE_BATCH_SIZE),
        desc=f"factor {factor_name}",
        total=n_batches,
    ):
        _compute_for_factor_partial_tiles(
            factor_name,
            factor_df,
            tiles_df.iloc[batch : batch + TILE_BATCH_SIZE],
            std_area,
        )


class Command(BaseCommand):
    help = "Compute and save factors data."

    def handle(self, *args, **options):
        tiles_df = load_geodataframe_from_db(Tile.objects.all(), ["id"])
        cities_df = load_geodataframe_from_db(
            City.objects.all(), ["name"]
        )  # Retrieve the names and geom of all cities
        # Match crs between Tiles and Cities
        tiles_df.set_crs(epsg=3857, inplace=True)
        tiles_crs = tiles_df.crs
        cities_df.set_crs(epsg=2154, inplace=True)
        cities_df.to_crs(tiles_crs, inplace=True)

        selected_city = cities_df.iloc[3]  # pick a city
        print(f"Selected city: {selected_city['name']}")
        df = tiles_df.clip(
            selected_city.geometry
        )  # Retrieve the tiles that corresponds to the city

        for factor_name in tqdm(FACTORS.keys(), total=len(FACTORS), desc="factors"):
            compute_for_factor(factor_name, df)
