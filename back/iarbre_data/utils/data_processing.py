"""Utils to process GEOJSON and GeoPackage to add them in the DB."""

from itertools import islice

from shapely import unary_union
from functools import reduce
from django.contrib.gis.geos import GEOSGeometry, Point
from django.db import connection
import shapely
import geopandas as gpd
from tqdm import tqdm
import requests

from iarbre_data.models import Data
from iarbre_data.settings import SRID_DB, SRID_DOWNLOADED_DATA
from iarbre_data.utils.database import log_progress


def batched(iterable, n) -> None:
    """Batch data into tuples of length n. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def _select_rows(df: gpd.GeoDataFrame, actions: dict) -> gpd.GeoDataFrame:
    """
    Apply the row selection actions (filter, filters, exclude) to a GeoDataFrame.

    Args:
        df (GeoDataFrame): GeoDataFrame to select rows from.
        actions (dict): Actions to apply to the GeoDataFrame.

    Returns:
        df (GeoDataFrame): GeoDataFrame with selected rows.
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
    return df


def apply_actions(df: gpd.GeoDataFrame, actions: dict) -> gpd.GeoDataFrame:
    """
    Apply a sequence of actions to a Geometry.

    Args:
        df (GeoDataFrame): GeoDataFrame to apply actions to.
        actions (dict): Actions to apply to the GeoDataFrame.

    Returns:
        df (GeoDataFrame): GeoDataFrame with actions applied.
    """
    df = _select_rows(df, actions)
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
        df = gpd.GeoDataFrame({"geometry": [geometry]}, crs=SRID_DB)
    if actions.get("subdivide"):
        df = subdivide(df, actions["subdivide"])

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


SUBDIVIDE_BATCH_SIZE = 1000

SUBDIVIDE_QUERY = """
    SELECT g.i, ST_AsBinary(ST_Subdivide(
        ST_CollectionExtract(ST_MakeValid(ST_GeomFromWKB(g.wkb, %s)), 3), %s))
    FROM unnest(%s::bytea[]) WITH ORDINALITY AS g(wkb, i)
    ORDER BY g.i
"""


def subdivide(
    df: gpd.GeoDataFrame | gpd.GeoSeries, max_vertices: int = 256
) -> gpd.GeoDataFrame | gpd.GeoSeries:
    """
    Repair geometries and split them into pieces of at most max_vertices vertices.

    Args:
        df (GeoDataFrame | GeoSeries): Polygonal geometries to subdivide.
        max_vertices (int): Maximum number of vertices per piece.

    Returns:
        GeoDataFrame | GeoSeries: One row per piece, carrying the original row's
        index label and attributes, in input order.
    """
    geoms = df if isinstance(df, gpd.GeoSeries) else df.geometry
    srid = df.crs.to_epsg()
    positions, pieces = [], []
    with connection.cursor() as cursor:
        for start in range(0, len(geoms), SUBDIVIDE_BATCH_SIZE):
            wkbs = shapely.to_wkb(geoms.iloc[start : start + SUBDIVIDE_BATCH_SIZE])
            cursor.execute(
                SUBDIVIDE_QUERY,
                [srid, max_vertices, [bytes(w) for w in wkbs]],
            )
            for i, wkb in cursor.fetchall():
                positions.append(start + i - 1)
                pieces.append(shapely.from_wkb(bytes(wkb)))
    pieces = gpd.array.from_shapely(pieces, crs=df.crs)
    if isinstance(df, gpd.GeoSeries):
        return gpd.GeoSeries(
            pieces, index=df.index[positions], crs=df.crs, name=df.name
        )
    result = df.iloc[positions].copy()
    result[df.geometry.name] = pieces
    return result


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
            point = Point(lon, lat, srid=SRID_DOWNLOADED_DATA)
            point.transform(SRID_DB)
            return point
        else:
            return None

    except Exception as e:
        print(f'Geocoding error for "{address}": {e}')
        return None
