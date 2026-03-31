import geopandas
from multiprocessing import Pool, cpu_count
from django.contrib.gis.db.models.functions import Area, Intersection
from django.contrib.gis.geos import GEOSGeometry
from django.core.management import BaseCommand
from django.db.models import Sum
from tqdm import tqdm

from iarbre_data.utils.database import log_progress
from iarbre_data.models import Vegestrate, City
from iarbre_data.settings import SRID_MAPLIBRE, SRID_DB

STRATE_TREES = 3
STRATE_BUSHES = 2
STRATE_GRASS = 1

STRATE_MAPPING = {
    STRATE_TREES: "arborescent",
    STRATE_BUSHES: "arbustif",
    STRATE_GRASS: "herbacee",
}

PATHS = [
    "file_data/vegestrate/vegestrate_lyon_metropole_ir_02.gpkg",
]


def _fix_invalid(series):
    mask = ~series.is_valid
    if mask.any():
        series = series.copy()
        series[mask] = series[mask].buffer(0)
    return series


def simplify_geom(gdf: geopandas.GeoDataFrame) -> geopandas.GeoDataFrame:
    gdf.to_crs(SRID_DB, inplace=True)
    gdf["geometry"] = _fix_invalid(gdf["geometry"])
    gdf = gdf.explode(ignore_index=True)
    gdf["geometry"] = _fix_invalid(gdf["geometry"])
    gdf["geometry"] = gdf["geometry"].simplify(tolerance=0.5)
    gdf["map_geometry"] = gdf.geometry.to_crs(SRID_MAPLIBRE)
    gdf["map_geometry"] = _fix_invalid(gdf["map_geometry"])
    return gdf


def process_vegestrate_data_in_chunks(gpkg_path: str, chunk_size: int = 50000) -> None:
    gdf_full = geopandas.read_file(gpkg_path)
    total_features = len(gdf_full)
    log_progress(f"Total features to process: {total_features}")

    chunks = [
        gdf_full.iloc[i : i + chunk_size].copy()
        for i in range(0, total_features, chunk_size)
    ]

    n_workers = min(cpu_count(), len(chunks))
    with Pool(processes=n_workers) as pool:
        processed_chunks = pool.map(simplify_geom, chunks)

    for gdf_chunk in tqdm(processed_chunks):
        save_vegestrate(gdf_chunk)


def save_vegestrate(vegestrate_datas: geopandas.GeoDataFrame) -> None:
    valid = vegestrate_datas[vegestrate_datas["class"].isin(STRATE_MAPPING)]

    veget_objects = []
    for geom_val, map_geom_val, class_val in zip(
        valid["geometry"], valid["map_geometry"], valid["class"]
    ):
        geom = GEOSGeometry(geom_val.wkb_hex)
        map_geom = GEOSGeometry(map_geom_val.wkb_hex)
        if geom.geom_type == "MultiPolygon":
            geom = geom[0]
        if map_geom.geom_type == "MultiPolygon":
            map_geom = map_geom[0]
        veget_objects.append(
            Vegestrate(
                geometry=geom,
                map_geometry=map_geom,
                strate=STRATE_MAPPING[class_val],
                surface=round(geom.area, 4),
            )
        )

    Vegestrate.objects.bulk_create(veget_objects)


def compute_city_vegetation_surfaces():
    log_progress("Computing vegetation surfaces for cities")
    cities_to_update = []
    for city in tqdm(City.objects.all(), desc="Computing city vegetation surfaces"):
        surfaces = {
            row["strate"]: float(row["total"].sq_m or 0.0)
            for row in (
                Vegestrate.objects.filter(geometry__intersects=city.geometry)
                .annotate(clipped_area=Area(Intersection("geometry", city.geometry)))
                .values("strate")
                .annotate(total=Sum("clipped_area"))
            )
        }
        city.trees_surface = surfaces.get(STRATE_MAPPING[STRATE_TREES], 0.0)
        city.bushes_surface = surfaces.get(STRATE_MAPPING[STRATE_BUSHES], 0.0)
        city.grass_surface = surfaces.get(STRATE_MAPPING[STRATE_GRASS], 0.0)
        city.total_vegetation_surface = (
            city.trees_surface + city.bushes_surface + city.grass_surface
        )
        cities_to_update.append(city)

    City.objects.bulk_update(
        cities_to_update,
        [
            "trees_surface",
            "bushes_surface",
            "grass_surface",
            "total_vegetation_surface",
        ],
    )


class Command(BaseCommand):
    help = "Import Vegestrate data in the DB."

    def handle(self, *args, **options):
        """Load Vegestrate data, compute stats for cities and save everything in DB."""
        log_progress("Cleaning Vegestrate model")
        print(Vegestrate.objects.all().delete())
        log_progress("Process and save large Vegestrate data in chunks")
        process_vegestrate_data_in_chunks(PATHS[0], chunk_size=5000)
        compute_city_vegetation_surfaces()
