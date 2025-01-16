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


def batched(iterable, n):
    """Batch data into tuples of length n. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def download_from_url(url, layer_name):
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
        gdf = gdf.to_crs(TARGET_PROJ)
    return gdf


def read_data(data_config):
    if data_config.get("url"):
        return download_from_url(data_config["url"], data_config["layer_name"])
    return gpd.read_file(DATA_DIR / data_config["file"])


def apply_actions(df, actions):
    """Apply a sequence of actions"""
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
    return df


def save_geometries(df: gpd.GeoDataFrame, data_config):
    datas = []
    actions_factors = zip(
        data_config.get("actions", [None]), data_config["factors"]
    )  # Default actions to None

    for actions, factor in actions_factors:
        sub_df = apply_actions(df.copy(), actions) if actions else df.copy()
        sub_df = sub_df.explode(index_parts=False)
        sub_df = sub_df[sub_df.geometry.type != "Point"]
        if len(sub_df) == 0:
            print(f"Factor: {factor} only contained Points")
            continue
        datas += [
            {"geometry": geometry, "factor": factor} for geometry in sub_df.geometry
        ]
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

    def add_arguments(self, parser):
        parser.add_argument(
            "--grid-size", type=int, default=5, help="Grid size in meters"
        )

    def handle(self, *args, **options):
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
                df = df.to_crs(TARGET_PROJ)  # Re_proj if needed
                df = df[
                    df.geometry.notnull() & df.geometry.is_valid
                ]  # Drop null or invalid geom
            except pyogrio.errors.DataSourceError:
                print(f"Error reading data {data_config['name']}")
                continue
            save_geometries(df, data_config)
            print(f"Data {data_config['name']} saved in {time.time() - start:.2f}s")
