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
    "Batch data into tuples of length n. The last batch may be shorter."
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def download_from_url(url, layer_name):
    params = dict(
        service="WFS",
        version="2.0.0",
        request="GetFeature",
        typeName=layer_name,
        outputFormat="GML3",
        crs=TARGET_PROJ,
    )
    content = requests.get(url, params=params, timeout=600).content
    # save content to bytes io and open with gp.GeoDataFrame.from_features
    io = BytesIO(content)
    return gpd.read_file(io)


def read_data(data_config):
    if data_config.get("url"):
        return download_from_url(data_config["url"], data_config["layer_name"])
    return gpd.read_file(DATA_DIR / data_config["file"])


def apply_action(df, action):
    if action.get("filter"):
        df = df[df[action["filter"]["name"]] == action["filter"]["value"]]
    if action.get("filters"):
        df = df[
            reduce(
                lambda x, y: x | y,
                [
                    df[filter_["name"]] == filter_["value"]
                    for filter_ in action["filters"]
                ],
            )
        ]
    if action.get("explode"):
        df = df.explode(index_parts=False)
    if action.get("buffer_size"):
        df = df.buffer(action["buffer_size"])
    if action.get("simplify"):
        df = df.simplify(action["simplify"])
    if action.get("union"):
        if isinstance(df, gpd.GeoDataFrame):
            df = df["geometry"]
        geometry = unary_union(df)
        df = gpd.GeoDataFrame({"geometry": [geometry]}, crs=TARGET_PROJ)
    return df


def save_geometries(df: gpd.GeoDataFrame, data_config):
    df = df.to_crs(TARGET_PROJ)
    datas = []
    for action, factor in zip(data_config.get("actions", []), data_config["factors"]):
        sub_df = apply_action(df.copy(), action)
        sub_df = sub_df.explode(index_parts=False)
        datas += [
            {"geometry": geometry, "factor": factor} for geometry in sub_df.geometry
        ]
    else: # no actions were configured, save data as is
        sub_df = df.copy().explode(index_parts=False)
        factor = data_config["factors"][0]
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
            "--grid-size", type=int, default=30, help="Grid size in meters"
        )

    def handle(self, *args, **options):
        for data_config in DATA_FILES + URL_FILES:
            if (qs := Data.objects.filter(metadata=data_config["name"])).count() > 0:
                print(
                    f"Data with metadata {data_config['name']} already exists ({qs.count()} rows). All deleted"
                )
                qs.delete()
            start = time.time()
            try:
                df = read_data(data_config)
            except pyogrio.errors.DataSourceError:
                print(f"Error reading data {data_config['name']}")
                continue
            save_geometries(df, data_config)
            print(f"Data {data_config['name']} saved in {time.time() - start:.2f}s")
