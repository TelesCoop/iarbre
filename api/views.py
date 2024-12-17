import time

from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET

from api.constants import ModelType
from api.map import territories_to_tile
from api.map import load_tiles
from iarbre_data.models import Tile

MODEL_BY_TYPE = {
    ModelType.TILE.value: Tile,
}


@require_GET
# @cache_page(60 * 60 * 24)
def tile_view(request, model_type, zoom, x, y):
    start_time = time.time()
    model = MODEL_BY_TYPE[model_type]
    # response = territories_to_tile(model, x, y, zoom)
    response = load_tiles(model, x, y, zoom)

    print(f"Request duration: {time.time() - start_time} seconds")
    return response
