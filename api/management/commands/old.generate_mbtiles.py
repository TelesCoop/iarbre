import geopandas as gpd
from django.core.management.base import BaseCommand
from shapely import wkt
from tqdm import tqdm

from iarbre_data.models import Tile


def convert_model_to_geodataframe(model, properties):
    queryset = model.objects.all()

    data = []
    for item in tqdm(queryset, total=len(queryset), desc="Converting model to json"):
        item_data = {
            'geometry': wkt.loads(item.geometry.wkt),
            "properties": {
                field_name: getattr(item, field_name)
                for field_name in properties
            }
        }
        data.append(item_data)

    gdf = gpd.GeoDataFrame(data, geometry='geometry', crs="EPSG:3857")
    return gdf

def convert_geodf_to_mbtiles_file(gdf, mbtiles_file_path):
    print("Converting GeoDataFrame to MBTiles file")
    gdf.to_file(mbtiles_file_path, driver="MBTiles", engine="pyogrio")


def convert_model_to_mbtiles(model, properties,  mbtiles_file_path):
    gdf = convert_model_to_geodataframe(model, properties)
    convert_geodf_to_mbtiles_file(gdf, mbtiles_file_path)

class Command(BaseCommand):
    help = "Convert Django model to MBTiles file"
    def handle(self, *args, **options):
        for (model, properties, file_name) in [
            (Tile, ["indice", "color"], "data/tiles.mbtiles"),
        ]:
            convert_model_to_mbtiles(model, properties, file_name)
