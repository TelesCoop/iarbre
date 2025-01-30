"""Save all land occupancy data to the database."""
import time
from functools import reduce
from io import BytesIO
from itertools import islice

import geopandas as gpd
import pyogrio
import requests
from django.contrib.gis.geos import GEOSGeometry
from django.core.management import BaseCommand
from shapely import unary_union
from tqdm import tqdm

from iarbre_data.data_config import DATA_FILES, URL_FILES
from iarbre_data.models import Data
from iarbre_data.settings import DATA_DIR, TARGET_PROJ


def batched(iterable, n) -> None:
    """Batch data into tuples of length n. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def download_from_url(url, layer_name):
    """
    Download data from a URL and return a GeoDataFrame.

    Args:
        url (str): URL to download data from
        layer_name (str): Name of the layer to download

    Returns:
        gdf (GeoDataFrame): GeoDataFrame with data from URL
    """
    if "wfs" in url.lower():
        params = dict(
            service="WFS",
            version="2.0.0",
            request="GetFeature",
            typeName=layer_name,
            outputFormat="GML3",
            crs=TARGET_PROJ,
        )
        content = requests.get(url, params=params, timeout=600).content
        # save content to bytes io and open with gp.GeoDataFrame.read_file
        io = BytesIO(content)
        gdf = gpd.read_file(io)
    else:  # GeoJSON
        content = requests.get(url, timeout=600).content
        io = BytesIO(content)
        gdf = gpd.read_file(io)
    return gdf


def read_data(data_config):
    """Read data from a file or URL and return a GeoDataFrame
    Args:
        data_config (dict): Contains either URL of the data or path to the file.
    Returns:
        df (GeoDataFrame): Use TARGET_PROJ and null and not valid geometry are removed.
    """
    if data_config.get("url"):
        df = download_from_url(data_config["url"], data_config["layer_name"])
    else:
        df = gpd.read_file(DATA_DIR / data_config["file"])
    df = df.to_crs(TARGET_PROJ)  # Re_proj if needed
    df = df[df.geometry.notnull() & df.geometry.is_valid]  # Drop null or invalid geom
    return df


def apply_actions(df, actions):
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


def process_data(df: gpd.GeoDataFrame, data_config):
    """
    Process geometries.

    Args:
        df (GeoDataFrame): GeoDataFrame to be apply actions on.
        data_config (dict): Configuration of the data.

    Returns:
        datas (list): Processed data.
    """
    datas = []
    actions_factors = zip(
        data_config.get("actions", [{}]), data_config["factors"]
    )  # Default actions to None

    for actions, factor in actions_factors:
        sub_df = apply_actions(df.copy(), actions)
        if len(sub_df) == 0:
            print(f"Factor: {factor} only contained Points")
            continue
        datas += [
            {"geometry": geometry, "factor": factor} for geometry in sub_df.geometry
        ]
    return datas


def save_geometries(datas, data_config) -> None:
    """
    Save geometries to the database.

    Args:
        datas (GeoDataFrame): GeoDataFrame to save to the database.
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


class Command(BaseCommand):
    help = "Create grid and save it to DB"

    def handle(self, *args, **options):
        """Save all land occupancy data to the database."""
        for data_config in DATA_FILES + URL_FILES:
            if (qs := Data.objects.filter(metadata=data_config["name"])).count() > 0:
                print(
                    f"Data with metadata {data_config['name']}"
                    f" already exists ({qs.count()} rows). All deleted"
                )
                qs.delete()
            start = time.time()
            try:
                df = read_data(data_config)
            except pyogrio.errors.DataSourceError:
                print(f"Error reading data {data_config['name']}")
                continue
            datas = process_data(df, data_config)
            save_geometries(datas, data_config)
            print(f"Data {data_config['name']} saved in {time.time() - start:.2f}s")
