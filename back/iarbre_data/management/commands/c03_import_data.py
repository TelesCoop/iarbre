"""Save all land occupancy data to the database."""
import time
import os
from datetime import datetime
from io import BytesIO
import geopandas as gpd
import pandas as pd
import pyogrio
import requests
from django.core.management import BaseCommand
from tqdm import tqdm
from iarbre_data.data_config import DATA_FILES, URL_FILES
from iarbre_data.models import Data
from iarbre_data.settings import DATA_DIR, TARGET_PROJ
from iarbre_data.management.commands.utils import select_city, log_progress
from iarbre_data.management.commands.utils_data import (
    process_data,
    save_geometries,
)


def download_dbtopo(url: str) -> gpd.GeoDataFrame:
    """
    Download Batiments from IGN BD TOPO V3.

    Args:
        url (str): URL to download data from

    Returns:
        gdf (GeoDataFrame): GeoDataFrame with data from URL
    """
    current_year = datetime.now().strftime("%Y")
    file_path = f"file_data/batiments_{current_year}.geojson"
    if os.path.isfile(file_path):
        gdf = gpd.read_file(file_path)
    else:  # Load data
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
            bbox = ",".join(map(str, city.geometry.bounds))
            params["BBOX"] = bbox + ",EPSG:2154"
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
                geom = tmp_gdf[
                    "geometry"
                ].force_2d()  # We don't need height of the buildings
                geom.name = (
                    "geometry"  # Restore name that has been erased by `force_2d`
                )
                all_geometries.append(geom)
                start_index += 5000

        gdf = gpd.GeoDataFrame(
            pd.concat(all_geometries, ignore_index=True), crs="EPSG:2154"
        )
        gdf.to_file(file_path, driver="GeoJSON")
    return gdf


def download_cerema(url: str) -> gpd.GeoDataFrame:
    """
    Download Friches from CEREMA API.

    Args:
        url (str): URL to download data from

    Returns:
        gdf (GeoDataFrame): GeoDataFrame with data from URL
    """

    current_year = datetime.now().strftime("%Y")
    file_path = f"file_data/cartofriches_{current_year}.geojson"
    if os.path.isfile(file_path):
        gdf = gpd.read_file(file_path)
    else:  # Load data
        coddep = "69"
        cities = select_city(None)

        cities.crs = 2154
        cities_4326 = cities.to_crs(4326)
        combined_gdf = gpd.GeoDataFrame()

        max_retries = 3  # Number of retries, CEREMA API is not always reliable
        backoff_factor = 2  # Exponential wait if fail to avoid hitting API limits

        all_geometries = []
        for city in tqdm(cities_4326.itertuples()):
            bbox = ",".join(map(str, city.geometry.bounds))
            params = {
                "coddep": coddep,
                "code_insee": int(city.code),
                "in_bbox": bbox,
                "page_size": 1000,
            }
            for attempt in range(max_retries):
                try:
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    break  # Exit the loop if successful
                except requests.exceptions.Timeout:
                    print(f"Timeout occurred, retrying {attempt + 1}/{max_retries}...")
                except requests.exceptions.RequestException as e:
                    print(f"Request failed: {e}")
                    break
                time.sleep(backoff_factor**attempt)  # Wait before retrying

            if response.status_code != 200:
                raise Exception(
                    f"Error for Cartofriche: {response.status_code}, {response.text}"
                )
            tmp_gdf = gpd.read_file(BytesIO(response.content))
            all_geometries.append(tmp_gdf[["geometry"]])

            combined_gdf = pd.concat([combined_gdf, tmp_gdf], ignore_index=True)
            time.sleep(1)  # Avoid hitting API rate limits
        gdf = gpd.GeoDataFrame(pd.concat(all_geometries, ignore_index=True))
        gdf.crs = 4326
        gdf = gdf.to_crs(2154)
        gdf.to_file(file_path, driver="GeoJSON")
    return gdf


def download_from_url(url: str, layer_name: str) -> gpd.GeoDataFrame:
    """
    Download data from a URL.

    Args:
        url (str): URL to download data from
        layer_name (str): Name of the layer to download

    Returns:
        gdf (GeoDataFrame): GeoDataFrame with data from URL
    """
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

    return gdf


def read_data(data_config: dict) -> gpd.GeoDataFrame:
    """Read data from a file or URL and return a GeoDataFrame.

    Args:
        data_config (dict): Contains either URL of the data or path to the file.

    Returns:
        df (GeoDataFrame): Use TARGET_PROJ and null and not valid geometry are removed.
    """
    if data_config.get("url"):
        if "data.geopf" in data_config.get("url").lower():  # BD TOPO
            df = download_dbtopo(data_config["url"])
        elif "cerema" in data_config.get("url").lower():
            df = download_cerema(data_config["url"])
        else:
            df = download_from_url(data_config["url"], data_config["layer_name"])
    elif data_config.get("layer_name"):
        df = gpd.read_file(
            DATA_DIR / data_config["file"], layer=data_config.get("layer_name")
        )
        df["geometry"] = df.geometry.force_2d()
    else:
        df = gpd.read_file(DATA_DIR / data_config["file"])
    df = df.to_crs(TARGET_PROJ)  # Re_proj if needed
    return df[df.geometry.notnull() & df.geometry.is_valid]  # Drop null or invalid geom


class Command(BaseCommand):
    help = "Create grid and save it to DB"

    def handle(self, *args, **options):
        """Save all land occupancy data to the database."""
        data_configs = DATA_FILES + URL_FILES
        for data_config in data_configs:
            if (qs := Data.objects.filter(metadata=data_config["name"])).count() > 0:
                log_progress(
                    f"Data with metadata {data_config['name']}"
                    f" already exists ({qs.count()} rows). All deleted"
                )
                qs.delete()
            start = time.time()
            try:
                log_progress(
                    f"Loading data {data_config['name']}, factors {data_config['factors']}"
                )
                df = read_data(data_config)
            except pyogrio.errors.DataSourceError:
                print(f"Error reading data {data_config['name']}")
                continue
            log_progress("Processing data.")
            datas = process_data(df, data_config)
            log_progress("Saving geom data.")
            save_geometries(datas, data_config)
            log_progress(
                f"Data {data_config['name']} saved in {time.time() - start:.2f}s", True
            )
