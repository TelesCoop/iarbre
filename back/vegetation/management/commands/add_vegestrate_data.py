import geopandas
from django.contrib.gis.db.models.functions import Area, Intersection
from django.contrib.gis.geos import GEOSGeometry
from django.core.management import BaseCommand
from django.db.models import Sum
from tqdm import tqdm

from iarbre_data.utils.database import log_progress
from iarbre_data.models import Vegestrate, City
from iarbre_data.settings import TARGET_MAP_PROJ, TARGET_PROJ
from iarbre_data.utils.data_processing import make_valid

STRATE_TREES = 3
STRATE_BUSHES = 2
STRATE_GRASS = 1

STRATE_MAPPING = {
    STRATE_TREES: "arborescent",
    STRATE_BUSHES: "arbustif",
    STRATE_GRASS: "herbacee",
}

PATHS = [
    "file_data/vegestrate/vegestrate_lyonmetro_02m.gpkg",
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


def process_vegestrate_data_in_chunks(gpkg_path: str, chunk_size: int = 50000) -> None:
    """Process and save large shapefile in chunks.

    Args:
        gpkg_path (str): Path to the geopackage to load.
        chunk_size (int): Number of rows to process at a time.

    Returns:
        None
    """

    gdf_full = geopandas.read_file(gpkg_path)
    total_features = len(gdf_full)
    log_progress(f"Total features to process: {total_features}")

    for start_idx in tqdm(range(0, total_features, chunk_size)):
        end_idx = min(start_idx + chunk_size, total_features)

        gdf_chunk = gdf_full.iloc[start_idx:end_idx].copy()
        gdf_chunk = simplify_geom(gdf_chunk)
        save_vegestrate(gdf_chunk)

        del gdf_chunk


def save_vegestrate(vegestrate_datas: geopandas.GeoDataFrame) -> None:
    """Save Vegestrate data to the database.

    Args:
        vegestrate_datas (GeoDataFrame): GeoDataFrame to save to the database.

    Returns:
        None
    """
    batch_size = 10000
    for start in range(0, len(vegestrate_datas), batch_size):
        end = start + batch_size
        batch = vegestrate_datas.loc[start:end]

        veget_objects = []
        for _, data in batch.iterrows():
            strate = STRATE_MAPPING.get(data["class"])

            if strate is None:
                continue

            geom = GEOSGeometry(data["geometry"].wkt)
            map_geom = GEOSGeometry(data["map_geometry"].wkt)
            if geom.geom_type == "MultiPolygon":
                geom = geom[0]
            if map_geom.geom_type == "MultiPolygon":
                map_geom = map_geom[0]

            veget_objects.append(
                Vegestrate(
                    geometry=geom,
                    map_geometry=map_geom,
                    strate=strate,
                    surface=round(geom.area, 4),
                )
            )

        Vegestrate.objects.bulk_create(veget_objects)


def compute_city_vegetation_surfaces():
    log_progress("Computing vegetation surfaces for cities")
    for city in tqdm(City.objects.all(), desc="Computing city vegetation surfaces"):
        vegestrate_qs = Vegestrate.objects.filter(geometry__intersects=city.geometry)

        def get_surface_for_strate(strate_value: str) -> float:
            result = (
                vegestrate_qs.filter(strate=strate_value)
                .annotate(clipped_area=Area(Intersection("geometry", city.geometry)))
                .aggregate(total=Sum("clipped_area"))["total"]
            )
            return result.sq_m if result else 0.0

        trees = get_surface_for_strate(STRATE_MAPPING[STRATE_TREES])
        bushes = get_surface_for_strate(STRATE_MAPPING[STRATE_BUSHES])
        grass = get_surface_for_strate(STRATE_MAPPING[STRATE_GRASS])

        city.trees_surface = trees
        city.bushes_surface = bushes
        city.grass_surface = grass
        city.total_vegetation_surface = trees + bushes + grass
        city.save(
            update_fields=[
                "trees_surface",
                "bushes_surface",
                "grass_surface",
                "total_vegetation_surface",
            ]
        )


class Command(BaseCommand):
    help = "Import Vegestrate data in the DB."

    def handle(self, *args, **options):
        """Load Vegestrate data, and stats for cities and save them all in the DB."""
        log_progress("Cleaning Vegestrate model")
        print(Vegestrate.objects.all().delete())
        log_progress("Process and save large Vegestrate data in chunks")
        process_vegestrate_data_in_chunks(PATHS[0], chunk_size=5000)
        compute_city_vegetation_surfaces()
