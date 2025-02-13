import time

from django.contrib.gis.geos import GEOSGeometry
from django.core.management import BaseCommand
from django.db import transaction
from shapely.geometry import box
import geopandas as gpd
from tqdm import tqdm

from iarbre_data.data_config import FACTORS

from iarbre_data.management.commands.utils import load_geodataframe_from_db, select_city
from iarbre_data.models import Data, Tile, TileFactor, City

TILE_BATCH_SIZE = 10_000


def has_intersection(geom, tiles_index):
    """
    Check if a geometry intersects with any tile.

    Args:
        geom (shapely.geometry.base.BaseGeometry): Geometry to check.
        tiles_index (geopandas.GeoDataFrame.sindex):  R-tree spatial index of the tiles.

    Returns:
        bool: True if the geometry intersects with any tile, False otherwise.
    """
    if geom is None or geom.is_empty:
        return False
    bounding_box = box(*geom.bounds)
    return any(tiles_index.query(bounding_box))


def _compute_for_factor_partial_tiles(factor_df, tiles_df, std_area):
    """
    Compute and store the proportion of standard tile area occupied by a geographic factor.

    Args:
        factor_df (GeoDataFrame): GeoDataFrame containing factor geometries that will be
            intersected with tiles.
        tiles_df (GeoDataFrame): GeoDataFrame containing tile geometries.
        std_area (float): Standard tile area in square meters (m²).

    Returns:
        list[TileFactor]: List of TileFactor objects to be created in the database
    """
    # Filter polygons in the bounding box of the tiles
    tiles_index = tiles_df.sindex

    idx_intersect = factor_df.geometry.apply(
        lambda geom: has_intersection(geom, tiles_index)
    )
    possible_matches = factor_df[idx_intersect].copy()
    if len(possible_matches) > 0:
        df = tiles_df.clip(possible_matches)
        df["value"] = df.geometry.area / std_area
    else:
        df = gpd.GeoDataFrame(
            [], columns=["id", "value", "geometry"], geometry="geometry"
        )
    return df


def compute_for_factor(factor_name, tiles_df, std_area) -> None:
    """
    Compute and store factor coverage proportions for the provided tiles.

    Args:
        factor_name (str): Name of the geographic factor to process (e.g., 'Parking', 'Route')
        tiles_df (geodataframe): Geodataframe with tiles to process.
        std_area (float): Standard tile area in square meters (m²).

    Returns:
        None

    Notes:
        - Standard area is calculated from the first Tile object in database (all tiles have the same area).
    """

    # In case they already exist, remove factors only for the tiles within the current batch
    TileFactor.objects.filter(factor=factor_name, tile_id__in=tiles_df["id"]).delete()

    qs = Data.objects.filter(factor=factor_name)
    if not qs.exists():
        return
    factor_df = load_geodataframe_from_db(qs, [])

    # compute and store by batch of 10k tiles
    n_batches = len(tiles_df) // TILE_BATCH_SIZE + 1
    for batch in tqdm(
        range(0, len(tiles_df), TILE_BATCH_SIZE),
        desc=f"factor {factor_name}",
        total=n_batches,
    ):
        tiles_df = tiles_df[tiles_df.geometry.notnull() & tiles_df.geometry.is_valid]
        df = _compute_for_factor_partial_tiles(
            factor_df,
            tiles_df.iloc[batch : batch + TILE_BATCH_SIZE],
            std_area,
        )
        if len(df) > 0:
            # Do not add a TileFactor if it already exists in the DB
            existing_pairs = set(TileFactor.objects.values_list("id", "factor"))
            tile_factors = [
                TileFactor(tile_id=row.id, factor=factor_name, value=row.value)
                for row in df.itertuples(index=False)
                if (row.id, factor_name) not in existing_pairs
            ]
            with transaction.atomic():
                TileFactor.objects.bulk_create(tile_factors)


def process_city(city, FACTORS, std_area, delete) -> None:
    """
    Process a city to compute and store factor coverage proportions.

    Args:
        city (Pandas DataFrame): DataFrame containing city information.
        FACTORS (dict): Dictionary containing the factors to process.
        std_area (float): Standard tile area in square meters (m²).
        delete (bool): If True, delete already computed Tiles.

    Returns:
        Completion (int): 0 if already computed, 1 otherwise.
    """
    city_name = city.name
    if city.tiles_computed and delete is False:
        print(f"TileFactor already computed for city {city_name}.")
        return 0

    city_geometry = city.geometry.wkt
    print(f"Processing city: {city_name}")
    t = time.perf_counter()

    # Query and load data for the city
    tiles_queryset = Tile.objects.filter(
        geometry__intersects=GEOSGeometry(city_geometry)
    )
    tiles_df = load_geodataframe_from_db(tiles_queryset, ["id"])
    for factor_name in FACTORS.keys():
        compute_for_factor(factor_name, tiles_df, std_area)
    City.objects.filter(id=city.id).update(tiles_computed=True)
    print(f"Finished city {city_name}. Time taken: {time.perf_counter() - t}")
    return 1


class Command(BaseCommand):
    help = "Compute and save factors data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--insee_code_city",
            type=str,
            required=False,
            default=None,
            help="The INSEE code of the city or cities to process. If multiple cities, please separate with comma (e.g. --insee_code='69266,69382')",
        ),
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete already existing TileFactor.",
        )

    def handle(self, *args, **options):
        """Compute and save factor data for the selected city."""
        insee_code_city = options["insee_code_city"]
        delete = options["delete"]
        std_area = (
            Tile.objects.first().geometry.area
        )  # Standard area of a tile (always the same)
        selected_city = select_city(insee_code_city)
        t = time.perf_counter()
        for city in selected_city.itertuples():
            process_city(city, FACTORS, std_area, delete)
        print(f"Elapsed time: {time.perf_counter() - t}")
