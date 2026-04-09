"""Save all land occupancy data to the database."""

import time
import pyogrio
import geopandas as gpd
from django.core.management import BaseCommand
from iarbre_data.data_config import DATA_FILES, URL_FILES
from iarbre_data.models import Data
from iarbre_data.settings import DATA_DIR, SRID_DB
from iarbre_data.utils.database import log_progress
from iarbre_data.utils.data_processing import process_data, save_geometries
from iarbre_data.utils.download import (
    download_agence_ore,
    download_cerema,
    download_dbtopo,
    download_from_url,
)


def read_data(data_config: dict) -> gpd.GeoDataFrame:
    """Read data from a file or URL and return a GeoDataFrame.

    Args:
        data_config (dict): Contains either URL of the data or path to the file.

    Returns:
        df (GeoDataFrame): Use SRID_DB and null and not valid geometry are removed.
    """
    if url := data_config.get("url"):
        if "opendata.agenceore.fr" in url:
            df = download_agence_ore(url)
        elif "data.geopf" in url:
            df = download_dbtopo(url)
        elif "cerema" in url:
            df = download_cerema(url)
        else:
            df = download_from_url(url, data_config["layer_name"])
    elif data_config.get("layer_name"):
        df = gpd.read_file(
            DATA_DIR / data_config["file"], layer=data_config.get("layer_name")
        )
    else:
        df = gpd.read_file(DATA_DIR / data_config["file"])
    df["geometry"] = df.geometry.force_2d()
    df = df.to_crs(SRID_DB)
    return df[df.geometry.notnull() & df.geometry.is_valid]


class Command(BaseCommand):
    help = "Create grid and save it to DB"

    def handle(self, *args, **options):
        """Save all land occupancy data to the database."""
        data_configs = DATA_FILES + URL_FILES
        for data_config in data_configs:
            if data_config["name"] == "Local Climate Zone":
                continue
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
            except pyogrio.errors.DataSourceError as e:
                print(e)
                print(f"Error reading data {data_config['name']}")
                continue
            log_progress("Processing data.")
            datas = process_data(df, data_config)
            log_progress("Saving geom data.")
            save_geometries(datas, data_config)
            log_progress(
                f"Data {data_config['name']} saved in {time.time() - start:.2f}s", True
            )
