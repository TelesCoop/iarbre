from django.contrib.gis.geos import GEOSGeometry
from django.core.management import BaseCommand
from tqdm import tqdm
from shapely.strtree import STRtree
from shapely.geometry import box

from iarbre_data.data_config import FACTORS
from iarbre_data.management.commands.utils import load_geodataframe_from_db
from iarbre_data.models import City, Data, Tile, TileFactor

TILE_BATCH_SIZE = 10_000


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

    # Filter polygons in the bounding box of the tiles
    tiles_index = STRtree(tiles_df.geometry)

    def has_intersection(geom):
        if geom is None or geom.is_empty:
            return False
        bounding_box = box(*geom.bounds)
        return any(tiles_index.query(bounding_box))

    idx_intersect = factor_df.geometry.apply(has_intersection)
    possible_matches = factor_df[idx_intersect].copy()
    df = tiles_df.clip(possible_matches)
    df["value"] = df.geometry.area / std_area
    tile_factors = [
        TileFactor(tile_id=row.id, factor=factor_name, value=row.value)
        for row in df.itertuples()
    ]
    return tile_factors


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
