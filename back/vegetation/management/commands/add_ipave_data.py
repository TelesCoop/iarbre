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


def simplify_geom(gdf: geopandas.GeoDataFrame) -> geopandas.GeoDataFrame:
    """Simplify geometry.

    Args:
        gdf (str): Path to the file to load.

    Returns:
        geopandas.GeoDataFrame: The loaded shapefile as a GeoDataFrame.
    """
    gdf.to_crs(TARGET_PROJ, inplace=True)

    # Simple correction for invalid geometry
    gdf["geometry"] = gdf["geometry"].apply(make_valid)
    gdf = gdf.explode(ignore_index=True)
    gdf["geometry"] = gdf["geometry"].apply(make_valid)
    gdf["map_geometry"] = gdf.geometry.to_crs(TARGET_MAP_PROJ)
    # After re-projecting, some invalid geometry appears
    gdf["map_geometry"] = gdf["map_geometry"].apply(make_valid)
    return gdf


def process_ipave_data_in_chunks(shp_path: str, chunk_size: int = 50000) -> None:
    """Process and save large shapefile in chunks.

    Args:
        shp_path (str): Path to the shapefile to load.
        chunk_size (int): Number of rows to process at a time.

    Returns:
        None
    """

    gdf_full = geopandas.read_file(shp_path)
    total_features = len(gdf_full)
    log_progress(f"Total features to process: {total_features}")

    for start_idx in tqdm(range(0, total_features, chunk_size)):
        end_idx = min(start_idx + chunk_size, total_features)

        gdf_chunk = gdf_full.iloc[start_idx:end_idx].copy()
        gdf_chunk = simplify_geom(gdf_chunk)
        save_ipave(gdf_chunk)

        del gdf_chunk


def save_ipave(ipave_datas: geopandas.GeoDataFrame) -> None:
    """Save ipave data to the database.

    Args:
        ipave_datas (GeoDataFrame): GeoDataFrame to save to the database.

    Returns:
        None
    """
    batch_size = 10000
    for start in range(0, len(ipave_datas), batch_size):
        end = start + batch_size
        batch = ipave_datas.loc[start:end]

        ipave_objects = []
        for _, data in batch.iterrows():
            geom = GEOSGeometry(data["geometry"].wkt)
            map_geom = GEOSGeometry(data["map_geometry"].wkt)
            # If multiPolygon persists only take the first one
            if geom.geom_type == "MultiPolygon":
                geom = geom[0]
            if map_geom.geom_type == "MultiPolygon":
                map_geom = map_geom[0]

            ipave_objects.append(
                Ipave(
                    geometry=geom,
                    map_geometry=map_geom,
                    strate=data["strate"],
                    surface=round(data["surface_m2"], 4),
                )
            )

        Ipave.objects.bulk_create(ipave_objects)


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
            city.vegetation_voirie_total = data["v_veg_t_ha"]
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
        log_progress("Load KPIs data and add them to City")
        gdf_kpis = geopandas.read_file(PATHS[1])
        kpi_datas = simplify_geom(gdf_kpis)
        save_to_cities(kpi_datas)
        log_progress("KPIs added to City model")
        del gdf_kpis, kpi_datas
        log_progress("Cleaning Ipave model")
        print(Ipave.objects.all().delete())
        log_progress("Process and save large Ipave data in chunks")
        process_ipave_data_in_chunks(PATHS[0], chunk_size=5000)
