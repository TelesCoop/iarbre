"""Add new land occupancy data and update SLT + fibre."""

import time
import geopandas as gpd
from django.core.management import BaseCommand

from iarbre_data.data_config import UPDATES

from iarbre_data.models import Data
from iarbre_data.settings import DATA_DIR, TARGET_PROJ
from iarbre_data.utils.database import load_geodataframe_from_db
from iarbre_data.utils.data_processing import process_data, save_geometries


class Command(BaseCommand):
    help = "Update and add new OCS data"

    def handle(self, *args, **options):
        """Update and add new OCS data"""
        for data_config in UPDATES:
            qs = Data.objects.filter(metadata=data_config["name"])
            qs_gdf = load_geodataframe_from_db(qs, fields=[])
            qs_gdf.crs = TARGET_PROJ
            start = time.time()
            gdf = gpd.read_file(
                DATA_DIR / data_config["file"], layer=data_config.get("layer_name")
            )
            gdf["geometry"] = gdf.geometry.force_2d()
            gdf = gdf.to_crs(TARGET_PROJ)
            print("Processing data.")
            datas = process_data(gdf, data_config)
            datas_gdf = gpd.GeoDataFrame(
                datas, geometry=[data["geometry"] for data in datas], crs=TARGET_PROJ
            )
            print("Intersecting with existing data in the DB")
            qs_union = qs_gdf.geometry.unary_union
            datas_gdf_union = datas_gdf.geometry.unary_union
            difference = datas_gdf_union.difference(qs_union)
            difference = gpd.GeoSeries([difference]).explode(index_parts=True)
            valid_differences = [
                {"geometry": geom, "factor": "Réseau Fibre"}
                for geom in difference.geometry
                if geom is not None
            ]

            save_geometries(valid_differences, data_config)
            print(f"Data {data_config['name']} updated in {time.time() - start:.2f}s")
