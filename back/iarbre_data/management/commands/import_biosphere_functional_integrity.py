from iarbre_data.utils.database import log_progress
from django.core.management import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from iarbre_data.models import BiosphereFunctionalIntegrity
from iarbre_data.settings import TARGET_MAP_PROJ, TARGET_PROJ
from iarbre_data.utils.data_processing import make_valid, split_geometry_with_grid
from concurrent.futures import ThreadPoolExecutor

import geopandas
import os
import shutil
from tqdm import tqdm


def split_data(shp_folder, shp_filename, batch_folder) -> geopandas.GeoDataFrame:
    batch_size = 5_000
    gdf = geopandas.read_file(os.path.join(shp_folder, shp_filename))
    if os.path.exists(batch_folder):
        shutil.rmtree(batch_folder)
    os.mkdir(batch_folder)

    index = 0
    for start in tqdm(range(0, gdf.shape[0], batch_size)):
        end = start + batch_size
        batch = gdf.iloc[start:end]
        batch = batch.dissolve(by="class")
        batch.to_file(os.path.join(batch_folder, f"part_{index}.shp"))
        index += 1


def load_data(shp_path) -> geopandas.GeoDataFrame:
    """Open the shapefile for BiosphèreFunctionalIntegrity.

    Returns:
        geopandas.GeoDataFrame: The loaded shapefile as a GeoDataFrame.

    Raises:
        FileNotFoundError: If no folder with "lcz" in the name is found or no .shp file is found in the folder.
    """
    gdf = geopandas.read_file(shp_path)

    gdf = gdf[["class", "geometry"]]
    gdf.to_crs(TARGET_PROJ, inplace=True)
    gdf_filtered = gdf

    # Split large geometries using 100m x 100m grid
    def worker(row, progress):
        print(f"splitting row : { round(progress, 2) }%")
        split_geoms = split_geometry_with_grid(row.geometry, grid_size=100.0)
        for geom in split_geoms:
            split_geometries.append({**row.to_dict(), "geometry": geom})

    split_geometries = []
    with ThreadPoolExecutor(max_workers=64) as executor:
        for idx, row in gdf_filtered.iterrows():
            executor.submit(worker, row, 100.0 * idx / gdf_filtered.shape[0])
    gdf_filtered = geopandas.GeoDataFrame(
        split_geometries, geometry="geometry", crs=TARGET_PROJ
    )

    # Simple correction for invalid geometry
    gdf_filtered["geometry"] = gdf_filtered["geometry"].apply(make_valid)
    # Check and explode MultiPolygon geometries
    gdf_filtered = gdf_filtered.explode(ignore_index=True)
    gdf_filtered["geometry"] = gdf_filtered["geometry"].apply(make_valid)
    gdf_filtered["map_geometry"] = gdf_filtered.geometry.to_crs(TARGET_MAP_PROJ)
    # After re-projecting, some invalid geometry appears
    gdf_filtered["map_geometry"] = gdf_filtered["map_geometry"].apply(make_valid)
    gdf_filtered["class"] = gdf_filtered["class"].astype(str)
    return gdf_filtered


def save_geometries(lcz_datas: geopandas.GeoDataFrame) -> None:
    """Save LCZ to the database.

    Args:
        lcz_datas (GeoDataFrame): GeoDataFrame to saselectve to the database.

    Returns:
        None
    """
    batch_size = 10000
    for start in tqdm(range(0, len(lcz_datas), batch_size)):
        end = start + batch_size
        batch = lcz_datas.loc[start:end]
        data = next(batch.iterrows())[1]
        print(data["geometry"].wkt)
        BiosphereFunctionalIntegrity.objects.bulk_create(
            [
                BiosphereFunctionalIntegrity(
                    geometry=GEOSGeometry(data["geometry"].wkt),
                    map_geometry=GEOSGeometry(data["map_geometry"].wkt),
                    indice=data["class"],
                )
                for _, data in batch.iterrows()
            ]
        )


class Command(BaseCommand):
    help = "Import Biosphere Functionial Integrity data in the DB."

    def handle(self, *args, **options):
        """Load LCZ from CEREMA and then save all LCZ data in the DB."""
        shp_folder = "file_data/biosphere_functional_integrity"
        shp_filename = "MDL_Cosia_CarHab_4m.shp"

        log_progress("Split data")
        batch_folder = os.path.join(shp_folder, f"{shp_filename}_parts")
        if not os.path.exists(batch_folder):
            BiosphereFunctionalIntegrity.objects.all().delete()
            split_data(shp_folder, shp_filename, batch_folder)

        shp_files = [
            x for x in os.listdir(os.path.join(batch_folder)) if x.endswith(".shp")
        ]
        for shp_file in shp_files:
            log_progress(f"Load batch { shp_file }")
            lcz_data = load_data(os.path.join(batch_folder, shp_file))

            save_geometries(lcz_data)
            os.remove(os.path.join(batch_folder, shp_file))
        # log_progress("Clean model")
        # log_progress("Load data and pre-process them")
        # log_progress("Save geometries")
