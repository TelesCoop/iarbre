import os
import time

from django.http import FileResponse, HttpResponse, Http404
from django.views.decorators.http import require_GET

from api.constants import ModelType
from api.map import territories_to_tile
from api.utils.mbtiles import MBTilesHandler
from iarbre_data import settings
from iarbre_data.models import Tile

MODEL_BY_TYPE = {
    ModelType.TILE.value: Tile,
}
MAP_TILE_HANDLER_SINGLETON = {}

@require_GET
# @cache_page(60 * 60 * 24)
def tile_view(request, model_type, zoom, x, y):
    start_time = time.time()
    model = MODEL_BY_TYPE[model_type]
    response = territories_to_tile(model, x, y, zoom)

    print(f"Request duration: {time.time() - start_time} seconds")
    return response


def serve_mbtiles(request, tileset, z, x, y):
    """
    Django view to serve tiles from MBTiles

    :param tileset: Name of the tileset (corresponding to .mbtiles file)
    :param z: Zoom level
    :param x: X coordinate
    :param y: Y coordinate
    """


    print("lol", tileset, z, x, y)
    try:
        if tileset in MAP_TILE_HANDLER_SINGLETON:
            tile_handler = MAP_TILE_HANDLER_SINGLETON[tileset]
        else:
            MBTILES_DIR = os.path.join(settings.BASE_DIR, "data")
            mbtiles_path = os.path.join(MBTILES_DIR, f"{tileset}.mbtiles")
            print(f"MBTiles path: {mbtiles_path}")
            tile_handler = MBTilesHandler(mbtiles_path)
            MAP_TILE_HANDLER_SINGLETON[tileset] = tile_handler


        # Retrieve tile
        tile_data = tile_handler.get_vector_tile(int(z), int(x), int(y))

        # Serve tile
        if tile_data:
            print("Tile retrieved")

            return HttpResponse(
                tile_data,
                content_type='application/x-protobuf',
                # headers={
                #     'Access-Control-Allow-Origin': '*'
                # }
            )
        else:
            raise Http404("Tile not found")

    except Exception as e:
        # Log error for debugging
        print(f"MBTiles error: {e}")
        raise Http404("Error serving tile")
