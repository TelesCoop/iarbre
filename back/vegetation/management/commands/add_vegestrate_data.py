import gc
import logging
import fiona
import geopandas
import shapely
from multiprocessing import Pool, cpu_count
from django.contrib.gis.db.models import GeometryField
from django.contrib.gis.db.models.functions import Area, Intersection
from django.contrib.gis.geos import GEOSGeometry
from django.core.management import BaseCommand
from django.db.models import Func, Sum
from tqdm import tqdm

from iarbre_data.utils.database import log_progress
from iarbre_data.models import Vegestrate, City
from iarbre_data.settings import SRID_MAPLIBRE, SRID_DB

logger = logging.getLogger(__name__)

STRATE_TREES = 3
STRATE_BUSHES = 2
STRATE_GRASS = 1

STRATE_MAPPING = {
    STRATE_TREES: "arborescent",
    STRATE_BUSHES: "arbustif",
    STRATE_GRASS: "herbacee",
}


class MakeValid(Func):
    function = "ST_MakeValid"
    output_field = GeometryField(srid=SRID_DB)


PATHS = [
    "file_data/vegestrate/vegestrate_02_2023.gpkg",
]


def _log_memory(label: str = "") -> None:
    try:
        with open("/proc/self/status") as fh:
            for line in fh:
                if line.startswith("VmRSS:"):
                    logger.info("Memory [%s]: %s", label, line.split(":")[1].strip())
                    return
    except OSError:
        pass


def _fix_invalid(series):
    mask = ~series.is_valid
    if mask.any():
        series = series.copy()
        series[mask] = shapely.make_valid(series[mask].values)
    return series


def simplify_geom(gdf: geopandas.GeoDataFrame) -> geopandas.GeoDataFrame:
    n_coords = int(shapely.get_num_coordinates(gdf.geometry.values).sum())
    logger.info(
        "simplify_geom: starting on chunk with %d rows, %d vertices", len(gdf), n_coords
    )
    try:
        gdf.to_crs(SRID_DB, inplace=True)
        gdf["geometry"] = _fix_invalid(gdf["geometry"])
        gdf = gdf.explode(ignore_index=True)
        gdf["geometry"] = _fix_invalid(gdf["geometry"])
        gdf["geometry"] = gdf["geometry"].simplify(tolerance=0.5)
        gdf["map_geometry"] = gdf.geometry.to_crs(SRID_MAPLIBRE)
        gdf["map_geometry"] = _fix_invalid(gdf["map_geometry"])
        logger.info("simplify_geom: done, %d rows", len(gdf))
        return gdf
    except Exception:
        logger.exception("simplify_geom failed on chunk with %d rows", len(gdf))
        raise


def _iter_chunks(gpkg_path: str, chunk_size: int):
    with fiona.open(gpkg_path) as f:
        crs = f.crs
        chunk = []
        for feature in f:
            chunk.append(feature)
            if len(chunk) == chunk_size:
                yield geopandas.GeoDataFrame.from_features(chunk, crs=crs)
                chunk = []
        if chunk:
            yield geopandas.GeoDataFrame.from_features(chunk, crs=crs)


def process_vegestrate_data_in_chunks(gpkg_path: str, chunk_size: int = 50000) -> None:
    with fiona.open(gpkg_path) as f:
        total_features = len(f)
    log_progress(f"Total features to process: {total_features}")

    n_chunks = (total_features + chunk_size - 1) // chunk_size
    n_workers = min(cpu_count() // 4, n_chunks)
    logger.info(
        "Chunks: %d, workers: %d, chunk_size: %d", n_chunks, n_workers, chunk_size
    )
    _log_memory("before pool")

    chunk_idx = 0
    try:
        with Pool(processes=n_workers, maxtasksperchild=20) as pool:
            for chunk_idx, gdf_chunk in enumerate(
                tqdm(
                    pool.imap(simplify_geom, _iter_chunks(gpkg_path, chunk_size)),
                    total=n_chunks,
                )
            ):
                logger.info(
                    "Chunk %d/%d: %d rows received from worker",
                    chunk_idx + 1,
                    n_chunks,
                    len(gdf_chunk),
                )
                _log_memory(f"chunk {chunk_idx + 1}/{n_chunks}")
                save_vegestrate(gdf_chunk)
                gc.collect()
    except Exception:
        logger.exception("Processing failed at chunk %d/%d", chunk_idx + 1, n_chunks)
        raise


def save_vegestrate(vegestrate_datas: geopandas.GeoDataFrame) -> None:
    valid = vegestrate_datas[vegestrate_datas["class"].isin(STRATE_MAPPING)]
    logger.info(
        "save_vegestrate: %d/%d rows pass class filter",
        len(valid),
        len(vegestrate_datas),
    )

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

    try:
        Vegestrate.objects.bulk_create(veget_objects)
        logger.info("bulk_create: inserted %d objects", len(veget_objects))
    except Exception:
        logger.exception("bulk_create failed for %d objects", len(veget_objects))
        raise


def compute_city_vegetation_surfaces():
    import time

    log_progress("Computing vegetation surfaces for cities")
    cities = list(City.objects.all())
    total = len(cities)
    logger.info("compute_city_vegetation_surfaces: %d cities to process", total)
    _log_memory("before city loop")

    cities_to_update = []
    t0 = time.monotonic()
    for idx, city in enumerate(tqdm(cities, desc="Computing city vegetation surfaces")):
        surfaces = {
            row["strate"]: float(row["total"].sq_m or 0.0)
            for row in (
                Vegestrate.objects.filter(geometry__intersects=city.geometry)
                .annotate(
                    clipped_area=Area(
                        Intersection(MakeValid("geometry"), city.geometry)
                    )
                )
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

        if (idx + 1) % 100 == 0:
            elapsed = time.monotonic() - t0
            rate = (idx + 1) / elapsed
            remaining = (total - idx - 1) / rate if rate > 0 else 0
            logger.info(
                "City %d/%d — %.1f cities/s — ~%.0fs remaining",
                idx + 1,
                total,
                rate,
                remaining,
            )
            _log_memory(f"city {idx + 1}/{total}")

    logger.info(
        "compute_city_vegetation_surfaces: loop done in %.1fs, bulk_update starting",
        time.monotonic() - t0,
    )
    _log_memory("before bulk_update")
    City.objects.bulk_update(
        cities_to_update,
        [
            "trees_surface",
            "bushes_surface",
            "grass_surface",
            "total_vegetation_surface",
        ],
    )
    logger.info(
        "compute_city_vegetation_surfaces: done in %.1fs total",
        time.monotonic() - t0,
    )


class Command(BaseCommand):
    help = "Import Vegestrate data in the DB."

    def add_arguments(self, parser):
        parser.add_argument(
            "--only-city-surfaces",
            action="store_true",
            help="Skip cleaning and data import; only recompute city vegetation surfaces.",
        )

    def handle(self, *args, **options):
        """Load Vegestrate data, compute stats for cities and save everything in DB."""
        if not options["only_city_surfaces"]:
            log_progress("Cleaning Vegestrate model")
            deleted_count, _ = Vegestrate.objects.all().delete()
            logger.info("Deleted %d existing Vegestrate rows", deleted_count)
            log_progress("Process and save large Vegestrate data in chunks")
            process_vegestrate_data_in_chunks(PATHS[0], chunk_size=5000)
        compute_city_vegetation_surfaces()
