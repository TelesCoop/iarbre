import geopandas
import requests
import zipfile
import io
import os

from django.contrib.gis.geos import GEOSGeometry
from django.core.management import BaseCommand
from tqdm import tqdm

from iarbre_data.data_config import URL_FILES, LCZ
from iarbre_data.management.commands.utils import make_valid, select_city
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

    lcz_path = "file_data/lcz"
    if os.path.isdir(lcz_path) and any(os.listdir(lcz_path)):
        shp_files = [f for f in os.listdir(lcz_path) if f.endswith(".shp")]
        if shp_files:
            return
    response = requests.get(url)
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            os.makedirs("file_data/lcz", exist_ok=True)
            z.extractall("file_data/lcz")
    else:
        raise ValueError(f"Failed to download file from {url}")


def load_data():
    """Open the shapefile for LCZ.

    Returns:
        geopandas.GeoDataFrame: The loaded shapefile as a GeoDataFrame.

    Raises:
        FileNotFoundError: If no folder with "lcz" in the name is found or no .shp file is found in the folder.
    """
    lcz_path = "file_data/lcz"
    if not os.path.isdir(lcz_path):
        raise FileNotFoundError("No folder for 'lcz' found in 'file_data/' directory.")
    shp_file = None
    for file in os.listdir(lcz_path):
        if file.lower().endswith(".shp"):
            shp_file = file
            break
    if not shp_file:
        raise FileNotFoundError(f"No .shp file found in the folder '{lcz_path}'.")

    shp_path = os.path.join(lcz_path, shp_file)
    gdf = geopandas.read_file(shp_path)
    gdf = gdf[["lcz", "geometry"]]
    gdf.to_crs(TARGET_PROJ, inplace=True)
    # We have LCZ for the whole 69-Rhone and want to keep only for Lyon Metropole
    all_cities_boundary = select_city(None).unary_union
    gdf_filtered = gdf[gdf.geometry.intersects(all_cities_boundary)]

    # Simple correction for invalid geometry
    gdf_filtered["geometry"] = gdf_filtered["geometry"].apply(make_valid)
    # Check and explode MultiPolygon geometries
    # Clean geom nested polygons
    gdf_filtered = gdf_filtered.explode(ignore_index=True)
    gdf_filtered = gdf_filtered.dissolve(by="lcz").reset_index()
    gdf_filtered = gdf_filtered.explode(ignore_index=True)

    gdf_filtered["map_geometry"] = gdf_filtered.geometry.to_crs(TARGET_MAP_PROJ)
    # After re-projecting, some invalid geometry appears
    gdf_filtered["map_geometry"] = gdf_filtered["map_geometry"].apply(make_valid)
    gdf_filtered["lcz"] = gdf_filtered["lcz"].astype(str)
    return gdf_filtered


def save_geometries(lcz_datas: geopandas.GeoDataFrame) -> None:
    """Save LCZ to the database.

    Args:
        lcz_datas (GeoDataFrame): GeoDataFrame to save to the database.

    Returns:
        None
    """
    batch_size = 10000
    for start in tqdm(range(0, len(lcz_datas), batch_size)):
        end = start + batch_size
        batch = lcz_datas.iloc[start:end]
        Lcz.objects.bulk_create(
            [
                Lcz(
                    geometry=GEOSGeometry(data["geometry"].wkt),
                    map_geometry=GEOSGeometry(data["map_geometry"].wkt),
                    lcz_index=data["lcz"],
                    lcz_description=LCZ[data["lcz"]],
                )
                for _, data in batch.iterrows()
            ]
        )


class Command(BaseCommand):
    help = "Import LCZ data in the DB."

    def handle(self, *args, **options):
        """Load LCZ from CEREMA and then save all LCZ data in the DB."""
        print("Clean model")
        print(Lcz.objects.all().delete())
        print("Download data if needed")
        download_data()
        print("Load data and pre-process them")
        lcz_data = load_data()
        print("Save geometries")
        save_geometries(lcz_data)
