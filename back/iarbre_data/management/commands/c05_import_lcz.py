import geopandas
import requests
import zipfile
import io
import os

from django.contrib.gis.geos import GEOSGeometry
from django.core.management import BaseCommand
from tqdm import tqdm

from iarbre_data.data_config import URL_FILES, LCZ
from iarbre_data.models import Lcz
from iarbre_data.settings import TARGET_MAP_PROJ, TARGET_PROJ


def download_data():
    """
    Downloads the Local Climate Zone data from the specified URL and extracts it to the 'file_data/' directory.

    Raises:
        ValueError: If the URL for Local Climate Zone does not exist.
    """
    urls = URL_FILES
    name = "Local Climate Zone"
    url = None
    for data_config in urls:
        if data_config["name"] == name:
            url = data_config["url"]
            break
    if not url:
        raise ValueError("URL for Local Climate Zone does not exist.")

    # Check if a file with "lcz" in the name already exists in the directory
    existing_files = [f for f in os.listdir("file_data/") if "lcz" in f.lower()]
    if existing_files:
        print(f"LCZ data already in file_data: {existing_files}")
    else:
        response = requests.get(url)
        if response.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall("file_data/")
        else:
            raise ValueError(f"Failed to download file from {url}")


def load_data():
    """Open the shapefile for LCZ.

    Returns:
        geopandas.GeoDataFrame: The loaded shapefile as a GeoDataFrame.

    Raises:
        FileNotFoundError: If no folder with "lcz" in the name is found or no .shp file is found in the folder.
    """
    # Search for a folder with "lcz" in the name
    lcz_folder = None
    for folder in os.listdir("file_data/"):
        if "lcz" in folder.lower() and os.path.isdir(
            os.path.join("file_data/", folder)
        ):
            lcz_folder = folder
            break

    if not lcz_folder:
        raise FileNotFoundError("No folder for 'lcz' found in 'file_data/' directory.")

    # Search for a .shp file in the found folder
    shp_file = None
    for file in os.listdir(os.path.join("file_data/", lcz_folder)):
        if file.lower().endswith(".shp"):
            shp_file = file
            break

    if not shp_file:
        raise FileNotFoundError(f"No .shp file found in the folder '{lcz_folder}'.")

    # Load the shapefile
    shp_path = os.path.join("file_data/", lcz_folder, shp_file)
    gdf = geopandas.read_file(shp_path)
    gdf = gdf[["lcz", "geometry"]]
    gdf.to_crs(TARGET_PROJ, inplace=True)
    gdf["map_geometry"] = gdf.geometry.to_crs(TARGET_MAP_PROJ)
    gdf["lcz"] = gdf["lcz"].astype(str)
    return gdf


def save_geometries(lcz_datas: geopandas.GeoDataFrame) -> None:
    """Save LCZ to the database.

    Args:
        lcz_datas (GeoDataFrame): GeoDataFrame to save to the database.

    Returns:
        None
    """
    batch_size = 1000
    for start in tqdm(range(0, len(lcz_datas), batch_size)):
        end = start + batch_size
        batch = lcz_datas.iloc[start:end]
        Lcz.objects.bulk_create(
            [
                Lcz(
                    geometry=GEOSGeometry(data["geometry"].wkt),
                    map_geometry=GEOSGeometry(data["map_geometry"].wkt),
                    lcz_indice=data["lcz"],
                    lcz_description=LCZ[data["lcz"]],
                )
                for _, data in batch.iterrows()
            ]
        )


class Command(BaseCommand):
    help = "Import LCZ data in the DB."

    def handle(self, *args, **options):
        """Save all LCZ data in the DB."""
        download_data()
        lcz_data = load_data()
        save_geometries(lcz_data)
