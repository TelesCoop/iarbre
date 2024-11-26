import gc
import multiprocessing
import os
from functools import partial

from django.contrib.gis.geos import GEOSGeometry
from django.core.management import BaseCommand
from tqdm import tqdm
import geopandas as gpd
from shapely.strtree import STRtree
from shapely.geometry import box

import time

from iarbre_data.data_config import FACTORS
from iarbre_data.management.commands.utils import load_geodataframe_from_db
from iarbre_data.models import City, Data, Tile, TileFactor

TILE_BATCH_SIZE = 10000
num_cpus = min(4, os.cpu_count() - 2)  # Limit parallel processes
#TILE_BATCH_SIZE = TILE_BATCH_SIZE // num_cpus

def calculate_intersection_length(tile, factor_df):
    """Intersection length between a Polygon and a LineString"""
    intersecting_lines = factor_df.geometry.apply(lambda line: tile.intersection(line))
    intersecting_lines = intersecting_lines[intersecting_lines.type == "LineString"]
    return sum(line.length for line in intersecting_lines), intersecting_lines

def _compute_for_factor_partial_tiles(factor_name, factor_df, tiles_df, std_area):
    """Compute and store the proportion of standard tile area occupied by a geographic factor.
    Args:
        factor_name (str): Name of the factor (e.g., 'Parking', 'Route') to process
        factor_df (GeoDataFrame): GeoDataFrame containing factor geometries that will be
            intersected with tiles.
        tiles_df (GeoDataFrame): GeoDataFrame containing tile geometries.
        std_area (float): Standard tile area in square meters (m²).
    """

    polygon_gdf = factor_df[factor_df.geometry.type.isin(["Polygon", "MultiPolygon", "Point"])]
    # linestring_gdf = factor_df[factor_df.geometry.type.isin(["LineString", "MultiLineString"])]
    if not polygon_gdf.empty:
        t = time.perf_counter()
        # Filter polygons in the bounding box of the tiles
        tiles_index = STRtree(tiles_df.geometry)
        def has_intersection(geom):
            if geom is None or geom.is_empty:
                return False
            bounding_box = box(*geom.bounds)
            return any(tiles_index.query(bounding_box))

        idx_intersect = polygon_gdf.geometry.apply(has_intersection)
        possible_matches = polygon_gdf[idx_intersect].copy()
        df = tiles_df.clip(possible_matches)
        df["value"] = df.geometry.area / std_area
    """
    elif not linestring_gdf.empty: # For Line geometry
        intersect = tiles_df.geometry.apply(lambda tile: linestring_gdf.geometry.intersects(tile).any())
        df_lines = tiles_df[intersect]
        df_lines["value"] = df_lines.geometry.apply(partial(calculate_intersection_length, factor_df=linestring_gdf))
    if not polygon_gdf.empty and not linestring_gdf.empty:
        df = pd.concat([df_polygons, df_lines], ignore_index=True)
    elif not polygon_gdf.empty:
        df = df_polygons
    elif not linestring_gdf.empty:
        df = df_lines
    else:
       raise TypeError("No valid geometry to process in factor_df.")
    """
    tile_factors = [
        TileFactor(tile_id=row.id, factor=factor_name, value=row.value)
        for row in df.itertuples()
    ]
    return tile_factors


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
    # compute and store by batch of 10k tiles
    n_batches = len(tiles_df) // TILE_BATCH_SIZE + 1
    for batch in tqdm(
        range(0, len(tiles_df), TILE_BATCH_SIZE),
        desc=f"factor {factor_name}",
        total=n_batches,
    ):
        tile_factors = _compute_for_factor_partial_tiles(
            factor_name,
            factor_df,
            tiles_df.iloc[batch : batch + TILE_BATCH_SIZE],
            std_area,
        )
        TileFactor.objects.bulk_create(tile_factors)

    """
    for i in range(0, len(tiles_df), TILE_BATCH_SIZE):
        batch = tiles_df.iloc[i : i + TILE_BATCH_SIZE]
        args = (factor_name, factor_df, batch, std_area)

        with multiprocessing.Pool(num_cpus) as pool:
            tile_factors = pool.map(process_batch, [args])

        # Flatten the result if process_batch returns a list of lists
        flat_tile_factors = [item for sublist in tile_factors for item in sublist]

        TileFactor.objects.bulk_create(flat_tile_factors, batch_size=1000)
        del flat_tile_factors
        del tile_factors
        gc.collect()
    """


class Command(BaseCommand):
    help = "Compute and save factors data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--insee_code_city",
            type=str,
            required=False,
            default=None,
            help="The INSEE code of the city or cities to process. If multiple cities, please separate with comma (e.g. --insee_code='69266,69382')",
        )

    def handle(self, *args, **options):
        insee_code_city = options["insee_code_city"]
        std_area = (
            Tile.objects.first().geometry.area
        )  # Standard area of a tile (always the same)

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
            city_geometry = city.geometry
            tiles_queryset = Tile.objects.filter(
                geometry__intersects=GEOSGeometry(city_geometry.wkt)
            )
            tiles_df = load_geodataframe_from_db(tiles_queryset, ["id"])
            for factor_name in tqdm(FACTORS.keys(), total=len(FACTORS), desc="factors"):
                compute_for_factor(factor_name, tiles_df, std_area)
            gc.collect()
