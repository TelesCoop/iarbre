"""Utils to process GEOJSON and GeoPackage to add them in the DB."""

from itertools import islice

from shapely import unary_union
from shapely.geometry import LineString
from shapely.ops import split
from functools import reduce
from django.contrib.gis.geos import GEOSGeometry, Point
import shapely
import geopandas as gpd
from tqdm import tqdm
import requests

from iarbre_data.models import Data
from iarbre_data.settings import TARGET_PROJ
from iarbre_data.utils.database import log_progress


def batched(iterable, n) -> None:
    """Batch data into tuples of length n. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def apply_actions(df: gpd.GeoDataFrame, actions: dict) -> gpd.GeoDataFrame:
    """
    Apply a sequence of actions to a Geometry.

    Args:
        df (GeoDataFrame): GeoDataFrame to apply actions to.
        actions (dict): Actions to apply to the GeoDataFrame.

    Returns:
        df (GeoDataFrame): GeoDataFrame with actions applied.
    """
    if actions.get("filter"):
        df = df[df[actions["filter"]["name"]] == actions["filter"]["value"]]
    if actions.get("filters"):
        df = df[
            reduce(
                lambda x, y: x | y,
                [
                    df[filter_["name"]] == filter_["value"]
                    for filter_ in actions["filters"]
                ],
            )
        ]
    if actions.get("exclude"):
        if type(actions["exclude"]["value"]) is list:
            df = df[~df[actions["exclude"]["name"]].isin(actions["exclude"]["value"])]
        else:
            df = df[df[actions["exclude"]["name"]] != actions["exclude"]["value"]]
    if actions.get("explode"):
        df = df.explode(index_parts=False)
    if actions.get("buffer_size"):
        df = df.buffer(actions["buffer_size"])
    if actions.get("buffer"):
        buffer_distances = df[actions["buffer"]["distance_column"]]
        if "_cm" in actions["buffer"]["distance_column"]:
            buffer_distances /= 100
        df = df.buffer(buffer_distances)
    if actions.get("simplify"):
        df = df.simplify(actions["simplify"])
    if actions.get("union"):
        if isinstance(df, gpd.GeoDataFrame):
            df = df["geometry"]
        geometry = unary_union(df)
        df = gpd.GeoDataFrame({"geometry": [geometry]}, crs=TARGET_PROJ)

    # Transform in Polygon
    df = df.explode(index_parts=False)
    df = df[df.geometry.type == "Polygon"]
    return df


def process_data(df: gpd.GeoDataFrame, data_config: dict) -> list:
    """
    Process geometries.

    Args:
        df (GeoDataFrame): GeoDataFrame to apply actions on.
        data_config (dict): Configuration of the data.

    Returns:
        datas (list): Processed data.
    """
    datas = []
    actions_factors = zip(
        data_config.get("actions", [{}]), data_config["factors"]
    )  # Default actions to None
    for actions, factor in actions_factors:
        log_progress(f"Start actions: {actions}")
        sub_df = apply_actions(df.copy(), actions)
        if len(sub_df) == 0:
            print(f"Factor: {factor} only contained Points")
            continue
        datas += [
            {"geometry": geometry, "factor": factor} for geometry in sub_df.geometry
        ]
    return datas


def save_geometries(datas: list[dict], data_config: dict) -> None:
    """
    Save geometries to the database.

    Args:
        datas (list[dict]): List of dictionaries containing geometries and metadata to save to the database.
        data_config (dict): Configuration of the data.

    Returns:
        None
    """
    for ix, batch in enumerate(tqdm(batched(datas, 1000))):
        Data.objects.bulk_create(
            [
                Data(
                    **{
                        **data,
                        "geometry": GEOSGeometry(data["geometry"].wkt),
                        "metadata": data_config["name"],
                    }
                )
                for data in batch
            ]
        )


def make_valid(
    geometry: shapely.geometry.base.BaseGeometry,
) -> shapely.geometry.base.BaseGeometry:
    """
    Fix minor topology errors in a geometry, such as a Polygon not being closed.
    Args:
        geometry (shapely.geometry.base.BaseGeometry): The geometry to be validated.
    Returns:
        shapely.geometry.base.BaseGeometry: The validated geometry.
    """
    if geometry and not geometry.is_valid:
        return geometry.buffer(0)
    return geometry


def split_geometry_with_grid(
    geometry: shapely.geometry.base.BaseGeometry, grid_size: float = 100.0
) -> list:
    """
    Split a geometry using a grid pattern.

    Args:
        geometry: The geometry to split
        grid_size: Size of grid cells in meters (default 100m)

    Returns:
        List of split geometries
    """
    if geometry.is_empty or not geometry.is_valid:
        return [geometry]

    # Get geometry bounds
    minx, miny, maxx, maxy = geometry.bounds

    # Create grid lines
    grid_lines = []

    # Vertical lines
    x = minx
    while x <= maxx:
        line = LineString([(x, miny - grid_size), (x, maxy + grid_size)])
        grid_lines.append(line)
        x += grid_size

    # Horizontal lines
    y = miny
    while y <= maxy:
        line = LineString([(minx - grid_size, y), (maxx + grid_size, y)])
        grid_lines.append(line)
        y += grid_size

    # Split geometry with each grid line
    result = [geometry]
    for line in tqdm(grid_lines, desc="Splitting a large geom") :
        new_result = []
        for geom in result:
            if geom.intersects(line):
                split_geoms = split(geom, line)
                if hasattr(split_geoms, "geoms"):
                    new_result.extend(split_geoms.geoms)
                else:
                    new_result.append(split_geoms)
            else:
                new_result.append(geom)
        result = new_result

    # Filter out empty geometries
    return [geom for geom in result if not geom.is_empty]


def geocode_address(address: str) -> Point:
    """
    Geocode address using OpenStreetMap Nominatim API.

    Args:
        address (str): Address to geocode

    Returns:
        Point: Point geometry in Lambert-93 (EPSG:2154) or None if geocoding fails
    """
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "countrycodes": "fr",
    }
    headers = {"User-Agent": "iarbre-hotspot-importer/1.0"}

    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            # Convert to Lambert-93 (EPSG:2154) coordinates
            point = Point(lon, lat, srid=4326)
            point.transform(2154)
            return point
        else:
            return None

    except Exception as e:
        print(f'Geocoding error for "{address}": {e}')
        return None
