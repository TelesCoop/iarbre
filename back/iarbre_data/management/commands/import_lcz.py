"""Import LCZ from CEREMA."""

import geopandas
import requests
import zipfile
import io
import os
from collections import defaultdict
from django.contrib.gis.geos import GEOSGeometry
from django.core.management import BaseCommand
from tqdm import tqdm
from shapely.strtree import STRtree

from iarbre_data.data_config import URL_FILES, LCZ
from iarbre_data.utils.database import select_city, log_progress
from iarbre_data.models import Lcz
from iarbre_data.settings import TARGET_MAP_PROJ, TARGET_PROJ
from iarbre_data.utils.data_processing import make_valid


def _find_intersections(gdf_sorted: geopandas.GeoDataFrame) -> tuple:
    """Find intersecting geometries using spatial index."""
    tree = STRtree(gdf_sorted.geometry)
    print("STREEE found)")
    intersection_graph = defaultdict(set)
    overlapping_indices = set()

    for i, geom in tqdm(enumerate(gdf_sorted.geometry)):
        candidates = tree.query(geom)
        for j in candidates:
            if i != j and geom.intersects(gdf_sorted.geometry.iloc[j]):
                intersection_graph[i].add(j)
                overlapping_indices.add(i)
                overlapping_indices.add(j)

    print("Intersection found")
    return intersection_graph, overlapping_indices


def _process_overlapping_geometry(
    current, intersection_graph, orig_idx, original_to_new, processed, i
):
    """Process a single overlapping geometry by removing intersections with higher priority geometries."""
    for intersecting_orig_idx in intersection_graph[orig_idx]:
        if intersecting_orig_idx in original_to_new:
            intersecting_new_idx = original_to_new[intersecting_orig_idx]
            if intersecting_new_idx < i:
                if current.intersects(processed[intersecting_new_idx]):
                    current = current.difference(processed[intersecting_new_idx])
                    current = make_valid(current)
                    if current.is_empty or not current.is_valid:
                        return None
    return current


def resolve_overlaps(gdf: geopandas.GeoDataFrame) -> geopandas.GeoDataFrame:
    """Remove overlaps by giving priority to smaller geometries.

    Smaller LCZ zones are more specific and should take priority over
    large background zones that may intersect with multiple smaller ones.

    Args:
        gdf (geopandas.GeoDataFrame): GeoDataFrame with potentially overlapping geometries

    Returns:
        geopandas.GeoDataFrame: GeoDataFrame with non-overlapping geometries
    """
    if len(gdf) <= 1:
        return gdf

    gdf = gdf.copy()
    gdf["area"] = gdf.geometry.area
    gdf_sorted = gdf.sort_values("area", ascending=True).reset_index(drop=True)

    intersection_graph, overlapping_indices = _find_intersections(gdf_sorted)

    if not overlapping_indices:
        return gdf_sorted.drop("area", axis=1)

    overlapping_gdf = (
        gdf_sorted.loc[list(overlapping_indices)].copy().reset_index(drop=True)
    )
    non_overlapping_gdf = gdf_sorted.drop(overlapping_indices)
    print(f"Number of overlapping {len(overlapping_gdf)}")

    original_to_new = {
        orig_idx: new_idx for new_idx, orig_idx in enumerate(overlapping_indices)
    }

    processed = []
    for i, (orig_idx, geom) in tqdm(
        enumerate(zip(overlapping_indices, overlapping_gdf.geometry)),
        total=len(overlapping_indices),
        desc="Processing overlapping geometries",
    ):
        current = _process_overlapping_geometry(
            geom, intersection_graph, orig_idx, original_to_new, processed, i
        )

        if current is not None and not current.is_empty:
            processed.append(current)
        else:
            processed.append(overlapping_gdf.geometry.iloc[i].buffer(0).buffer(-1))

    overlapping_gdf.geometry = processed
    overlapping_gdf = overlapping_gdf[~overlapping_gdf.geometry.is_empty].reset_index(
        drop=True
    )

    result = geopandas.pd.concat(
        [non_overlapping_gdf, overlapping_gdf], ignore_index=True
    )
    return result.drop("area", axis=1)


def download_data() -> None:
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


def load_data() -> geopandas.GeoDataFrame:
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
    gdf = gdf[
        ["lcz", "geometry", "hre", "are", "bur", "ror", "bsr", "war", "ver", "vhr"]
    ]
    gdf.to_crs(TARGET_PROJ, inplace=True)
    # We have LCZ for the whole 69-Rhone and want to keep only for Lyon Metropole
    all_cities_boundary = select_city(None).union_all()
    gdf_filtered = gdf[gdf.geometry.intersects(all_cities_boundary)]
    gdf_filtered["geometry"] = gdf_filtered.geometry.intersection(all_cities_boundary)

    # Simple correction for invalid geometry
    gdf_filtered["geometry"] = gdf_filtered["geometry"].apply(make_valid)
    # Check and explode MultiPolygon geometries
    gdf_filtered = gdf_filtered.explode(ignore_index=True)
    # Resolve overlaps - smaller geometries take priority over larger ones
    gdf_filtered = resolve_overlaps(gdf_filtered)
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
        batch = lcz_datas.loc[start:end]
        Lcz.objects.bulk_create(
            [
                Lcz(
                    geometry=GEOSGeometry(data["geometry"].wkt),
                    map_geometry=GEOSGeometry(data["map_geometry"].wkt),
                    lcz_index=data["lcz"],
                    lcz_description=LCZ[data["lcz"]],
                    details={
                        "hre": data["hre"],
                        "are": data["are"],
                        "bur": data["bur"],
                        "ror": data["ror"],
                        "bsr": data["bsr"],
                        "war": data["war"],
                        "ver": data["ver"],
                        "vhr": data["vhr"],
                    },
                )
                for _, data in batch.iterrows()
            ]
        )


class Command(BaseCommand):
    help = "Import LCZ data in the DB."

    def handle(self, *args, **options):
        """Load LCZ from CEREMA and then save all LCZ data in the DB."""
        log_progress("Clean model")
        print(Lcz.objects.all().delete())
        log_progress("Download data if needed")
        download_data()
        log_progress("Load data and pre-process them")
        lcz_data = load_data()
        log_progress("Save geometries")
        save_geometries(lcz_data)
