import geopandas
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from iarbre_data.models import BiosphereFunctionalIntegrity
from iarbre_data.settings import SRID_DB, SRID_MAPLIBRE
from iarbre_data.utils.database import log_progress
from iarbre_data.utils.data_processing import make_valid
from tqdm import tqdm


SHP_PATH = "file_data/biosphere_functional_integrity/MDL_Cosia_CarHab_IFB_4m.shp"
BATCH_SIZE = 10_000


class Command(BaseCommand):
    help = "Import Biosphere Functional Integrity index from vectorized raster."

    def handle(self, *args, **options):
        log_progress("Delete existing data")
        BiosphereFunctionalIntegrity.objects.all().delete()

        log_progress("Load shapefile")
        gdf = geopandas.read_file(SHP_PATH)
        gdf = gdf[gdf["class"] >= 0].copy()
        gdf["indice"] = gdf["class"].astype(int)
        gdf = gdf.to_crs(SRID_DB)
        gdf["geometry"] = gdf["geometry"].apply(make_valid)
        gdf = gdf.explode(ignore_index=True)
        gdf["geometry"] = gdf["geometry"].apply(make_valid)
        gdf["map_geometry"] = gdf["geometry"].to_crs(SRID_MAPLIBRE)
        gdf["map_geometry"] = gdf["map_geometry"].apply(make_valid)

        log_progress("Save to database")
        for start in tqdm(range(0, len(gdf), BATCH_SIZE)):
            batch = gdf.iloc[start : start + BATCH_SIZE]
            BiosphereFunctionalIntegrity.objects.bulk_create(
                [
                    BiosphereFunctionalIntegrity(
                        geometry=GEOSGeometry(row["geometry"].wkt),
                        map_geometry=GEOSGeometry(row["map_geometry"].wkt),
                        indice=row["indice"],
                    )
                    for _, row in batch.iterrows()
                ]
            )
