"""Utils to process GEOJSON and GeoPackage to add them in the DB."""
from itertools import islice

from shapely import unary_union
from functools import reduce
from django.contrib.gis.geos import GEOSGeometry
import shapely
import geopandas as gpd
from tqdm import tqdm

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
        if type(actions["exclude"]["value"]) == list:
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
                        "factor": data["factor"],
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
