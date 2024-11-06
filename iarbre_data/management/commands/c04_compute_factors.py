import time
import os
from django.core.management import BaseCommand
from tqdm import tqdm
import multiprocessing

from iarbre_data.data_config import FACTORS
from iarbre_data.management.commands.utils import load_geodataframe_from_db
from iarbre_data.models import Data, Tile, TileFactor, City


TILE_BATCH_SIZE = 10_000


def _compute_for_factor_partial_tiles(factor_name, factor_df, tiles_df, std_area):
    """Compute and store the proportion of standard tile area occupied by a geographic factor.
    Args:
        factor_name (str): Name of the factor (e.g., 'Parking', 'Route') to process
        factor_df (GeoDataFrame): GeoDataFrame containing factor geometries that will be
            intersected with tiles.
        tiles_df (GeoDataFrame): GeoDataFrame containing tile geometries.
        std_area (float): Standard tile area in square meters (m²).
    """
    df = tiles_df.clip(factor_df)
    df["value"] = df.geometry.area / std_area
    tile_factors = [
        TileFactor(tile_id=row.id, factor=factor_name, value=row.value)
        for row in df.itertuples()
    ]
    TileFactor.objects.bulk_create(tile_factors)


def process_batch(args):
    """Helper func for multiprocessing"""
    factor_name, factor_df, batch, std_area = args
    return _compute_for_factor_partial_tiles(factor_name, factor_df, batch, std_area)


def compute_for_factor(factor_name, tiles_df, std_area):
    """Compute and store factor coverage proportions for the provided tiles.
    Args:
        factor_name (str): Name of the geographic factor to process (e.g., 'Parking', 'Route')
        tiles_df (GeoDataFrame): GeoDataFrame containing all tiles to process.
        std_area (float): Standard tile area in square meters (m²).
    Notes:
        - Standard area is calculated from the first Tile object in database (all tiles have the same area).
    """
    TileFactor.objects.filter(factor=factor_name).delete()  # remove former factors

    qs = Data.objects.filter(factor=factor_name)
    if not qs.exists():
        return
    factor_df = load_geodataframe_from_db(qs, [])
    factor_df.set_crs(epsg=3857, inplace=True)
    # Prepare batches
    batches = [
        tiles_df.iloc[i : i + TILE_BATCH_SIZE]
        for i in range(0, len(tiles_df), TILE_BATCH_SIZE)
    ]
    args_list = [(factor_name, factor_df, batch, std_area) for batch in batches]

    with multiprocessing.Pool(os.cpu_count() - 2) as pool: # Let 2 CPUs available
        pool.map(process_batch, args_list)


class Command(BaseCommand):
    help = "Compute and save factors data."

    def handle(self, *args, **options):
        std_area = (
            Tile.objects.first().geometry.area
        )  # Standard area of a tile (always the same)
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
            compute_for_factor(factor_name, df, std_area)
