import json
import os
import time
from datetime import datetime
from io import BytesIO

import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import shape
from tqdm import tqdm

from iarbre_data.settings import DATA_DIR, SRID_DB
from iarbre_data.utils.database import select_city

METROPOLE_LYON_EPCI = "200046977"


def _cache_path(name: str) -> str:
    current_year = datetime.now().strftime("%Y")
    return DATA_DIR / f"{name}_{current_year}.geojson"


def _load_or_fetch(file_path, fetch_fn) -> gpd.GeoDataFrame:
    if os.path.isfile(file_path):
        return gpd.read_file(file_path)
    gdf = fetch_fn()
    gdf.to_file(file_path, driver="GeoJSON")
    return gdf


def download_dbtopo(url: str) -> gpd.GeoDataFrame:
    def fetch():
        params = {
            "SERVICE": "WFS",
            "VERSION": "2.0.0",
            "REQUEST": "GetFeature",
            "TYPENAMES": "BDTOPO_V3:batiment",
            "SRSNAME": "EPSG:2154",
            "OUTPUTFORMAT": "text/xml; subtype=gml/3.2",
            "COUNT": 5000,
        }
        cities = select_city(None)
        all_geometries = []
        for city in tqdm(cities.itertuples()):
            params["BBOX"] = ",".join(map(str, city.geometry.bounds)) + ",EPSG:2154"
            start_index = 0
            while True:
                params["STARTINDEX"] = start_index
                response = requests.get(url, params=params, timeout=60)
                if response.status_code != 200:
                    raise Exception(
                        f"Error for BD TOPO: {response.status_code}, {response.text}"
                    )
                tmp_gdf = gpd.read_file(BytesIO(response.content))
                if tmp_gdf.empty:
                    break
                geom = tmp_gdf["geometry"].force_2d()
                geom.name = "geometry"
                all_geometries.append(geom)
                start_index += 5000
        return gpd.GeoDataFrame(
            pd.concat(all_geometries, ignore_index=True), crs="EPSG:2154"
        )

    return _load_or_fetch(_cache_path("batiments"), fetch)


def download_cerema(url: str) -> gpd.GeoDataFrame:
    def fetch():
        cities = select_city(None)
        cities.crs = 2154
        cities_4326 = cities.to_crs(4326)
        max_retries = 3
        backoff_factor = 2
        all_geometries = []
        for city in tqdm(cities_4326.itertuples()):
            params = {
                "coddep": "69",
                "code_insee": int(city.code),
                "in_bbox": ",".join(map(str, city.geometry.bounds)),
                "page_size": 1000,
            }
            for attempt in range(max_retries):
                try:
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    break
                except requests.exceptions.Timeout:
                    print(f"Timeout occurred, retrying {attempt + 1}/{max_retries}...")
                except requests.exceptions.RequestException as e:
                    print(f"Request failed: {e}")
                    break
                time.sleep(backoff_factor**attempt)
            if response.status_code != 200:
                raise Exception(
                    f"Error for Cartofriche: {response.status_code}, {response.text}"
                )
            all_geometries.append(
                gpd.read_file(BytesIO(response.content))[["geometry"]]
            )
            time.sleep(1)
        gdf = gpd.GeoDataFrame(pd.concat(all_geometries, ignore_index=True))
        gdf.crs = 4326
        return gdf.to_crs(2154)

    return _load_or_fetch(_cache_path("cartofriches"), fetch)


def download_from_url(url: str, layer_name: str) -> gpd.GeoDataFrame:
    params = dict(
        service="WFS",
        version="2.0.0",
        request="GetFeature",
        typeName=layer_name,
        outputFormat="GML3",
        crs=SRID_DB,
    )
    return gpd.read_file(BytesIO(requests.get(url, params=params, timeout=600).content))


def download_agence_ore(url: str) -> gpd.GeoDataFrame:
    slug = url.split("/datasets/")[1].split("/")[0]

    def fetch():
        params = {
            "size": 10000,
            "qs": f"code_epci:{METROPOLE_LYON_EPCI}",
            "format": "json",
        }
        geometries = []
        next_url = url
        while next_url:
            response = requests.get(next_url, params=params, timeout=120)
            response.raise_for_status()
            data = response.json()
            for record in data["results"]:
                geometries.append(shape(json.loads(record["geometry"])))
            next_url = data.get("next")
            params = None
        return gpd.GeoDataFrame(geometry=geometries, crs="EPSG:4326")

    return _load_or_fetch(_cache_path(slug), fetch)
