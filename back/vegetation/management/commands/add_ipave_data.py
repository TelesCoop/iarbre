"""Import iPVAVE data from Exo-Dev."""

import geopandas
from django.contrib.gis.geos import GEOSGeometry
from django.core.management import BaseCommand
from tqdm import tqdm

from iarbre_data.utils.database import log_progress
from iarbre_data.models import Ipave, City
from iarbre_data.settings import TARGET_MAP_PROJ, TARGET_PROJ
from iarbre_data.utils.data_processing import make_valid

PATHS = [
    "file_data/ipave/vegestrat_voirie.shp",
    "file_data/ipave/kpi_vegestrat_voirie.shp",
]


def load_data(shp_path: str) -> geopandas.GeoDataFrame:
    """Open the shapefile.

    Args:
        shp_path (str): Path to the file to load.

    Returns:
        geopandas.GeoDataFrame: The loaded shapefile as a GeoDataFrame.

    Raises:
        FileNotFoundError: If no path is incorrect.
    """
    gdf = geopandas.read_file(shp_path)

    gdf.to_crs(TARGET_PROJ, inplace=True)

    # Simple correction for invalid geometry
    gdf["geometry"] = gdf["geometry"].apply(make_valid)
    # Check and explode MultiPolygon geometries
    gdf = gdf.explode(ignore_index=True)
    gdf["geometry"] = gdf["geometry"].apply(make_valid)
    gdf["map_geometry"] = gdf.geometry.to_crs(TARGET_MAP_PROJ)
    # After re-projecting, some invalid geometry appears
    gdf["map_geometry"] = gdf["map_geometry"].apply(make_valid)
    return gdf


def save_ipave(ipave_datas: geopandas.GeoDataFrame) -> None:
    """Save ipave data to the database.

    Args:
        ipave_datas (GeoDataFrame): GeoDataFrame to save to the database.

    Returns:
        None
    """
    batch_size = 10000
    for start in tqdm(range(0, len(ipave_datas), batch_size)):
        end = start + batch_size
        batch = ipave_datas.loc[start:end]
        Ipave.objects.bulk_create(
            [
                Ipave(
                    geometry=GEOSGeometry(data["geometry"].wkt),
                    map_geometry=GEOSGeometry(data["map_geometry"].wkt),
                    strate=data["strate"],
                    surface=round(data["surface"], 4),
                )
                for _, data in batch.iterrows()
            ]
        )


def save_to_cities(kpi_datas: geopandas.GeoDataFrame) -> None:
    """Save KPIs data to the database.

    Args:
        kpi_datas (GeoDataFrame): GeoDataFrame to save to the database.

    Returns:
        None
    """
    cities_to_update = []
    for _, data in tqdm(kpi_datas.iterrows()):
        try:
            city = City.objects.get(code=data["insee"])
            city.vegetation_voirie_haute = data["v_veg_h_ha"]
            city.vegetation_voirie_moyenne = data["v_veg_m_ha"]
            city.vegetation_voirie_basse = data["v_veg_b_ha"]
            city.vegetation_voirie_total = data["v_veg_total_ha"]
            cities_to_update.append(city)
        except City.DoesNotExist:
            print(f"City {data['nom']} does not exist in the DB.")
            continue

    if cities_to_update:
        City.objects.bulk_update(
            cities_to_update,
            [
                "vegetation_voirie_haute",
                "vegetation_voirie_moyenne",
                "vegetation_voirie_basse",
                "vegetation_voirie_total",
            ],
        )


class Command(BaseCommand):
    help = "Import Ipave data in the DB."

    def handle(self, *args, **options):
        """Load Ipave data, and stats for cities and save them all in the DB."""
        log_progress("Clean model")
        print(Ipave.objects.all().delete())
        log_progress("Load data and pre-process them")
        ipave_data = load_data(PATHS[0])
        log_progress("Save geometries")
        save_ipave(ipave_data)
        log_progress("Load KPIs data and add them to City")
        kpi_datas = load_data(PATHS[1])
        save_to_cities(kpi_datas)
