from iarbre_data.utils.database import log_progress
from django.core.management import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from iarbre_data.models import BiosphereFunctionalIntegrityLandCover
from iarbre_data.settings import SRID_MAPLIBRE, SRID_DB
from iarbre_data.utils.data_processing import make_valid, subdivide
from iarbre_data.utils.biosphere_land_cover import CLASS_TO_LAND_COVER, CLASS_TO_BINARY

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
    """Open the shapefile for LandCover.

    Returns:
        geopandas.GeoDataFrame: The loaded shapefile as a GeoDataFrame.

    Raises:
        FileNotFoundError: If no folder with "lcz" in the name is found or no .shp file is found in the folder.
    """
    gdf = geopandas.read_file(shp_path)

    gdf = gdf[["class", "geometry"]]
    gdf.to_crs(SRID_DB, inplace=True)
    gdf_filtered = gdf

    gdf_filtered = subdivide(gdf_filtered)

    # Simple correction for invalid geometry
    gdf_filtered["geometry"] = gdf_filtered["geometry"].apply(make_valid)
    # Check and explode MultiPolygon geometries
    gdf_filtered = gdf_filtered.explode(ignore_index=True)
    gdf_filtered["geometry"] = gdf_filtered["geometry"].apply(make_valid)
    gdf_filtered["map_geometry"] = gdf_filtered.geometry.to_crs(SRID_MAPLIBRE)
    # After re-projecting, some invalid geometry appears
    gdf_filtered["map_geometry"] = gdf_filtered["map_geometry"].apply(make_valid)
    gdf_filtered["class"] = gdf_filtered["class"].astype(int)
    return gdf_filtered


def save_geometries(lcz_datas: geopandas.GeoDataFrame) -> None:
    """Save Land cover from COSIA + CARHAB to the database.

    Args:
        landcover_datas (GeoDataFrame): GeoDataFrame to save in the database.

    Returns:
        None
    """
    batch_size = 10000
    for start in tqdm(range(0, len(lcz_datas), batch_size)):
        end = start + batch_size
        batch = lcz_datas.iloc[start:end]
        BiosphereFunctionalIntegrityLandCover.objects.bulk_create(
            [
                BiosphereFunctionalIntegrityLandCover(
                    geometry=GEOSGeometry(data["geometry"].wkt),
                    map_geometry=GEOSGeometry(data["map_geometry"].wkt),
                    land_cover=CLASS_TO_LAND_COVER[data["class"]],
                    binary=CLASS_TO_BINARY[data["class"]],
                )
                for _, data in batch.iterrows()
                if data["class"] in CLASS_TO_LAND_COVER
            ]
        )


class Command(BaseCommand):
    help = "Import Land Cover data from COSIA + Carhab in the DB."

    def handle(self, *args, **options):
        """Load the shapefile produced by Emile to add it in the DB."""
        shp_folder = "file_data/biosphere_functional_integrity"
        shp_filename = "MDL_Cosia_CarHab_4m.shp"

        log_progress("Clean data")
        BiosphereFunctionalIntegrityLandCover.objects.all().delete()

        log_progress("Split data")
        batch_folder = os.path.join(shp_folder, f"{shp_filename}_parts")
        split_data(shp_folder, shp_filename, batch_folder)

        shp_files = [
            x for x in os.listdir(os.path.join(batch_folder)) if x.endswith(".shp")
        ]
        for shp_file in shp_files:
            log_progress(f"Load batch { shp_file }")
            landcover_data = load_data(os.path.join(batch_folder, shp_file))

            save_geometries(landcover_data)
        shutil.rmtree(batch_folder)
