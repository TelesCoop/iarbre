import time

from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET

from api.constants import ModelType
from api.map import load_tiles

MODEL_BY_TYPE = {
    ModelType.TILE.value: "tile",
}


@require_GET
@cache_page(60 * 60 * 24)
def tile_view(request, model_type, layer, zoom, x, y):
    """View to get tiles for a specific model type and layer.
    Params:
        model_type (str): Type of model to get tiles for.
        layer (str): Layer to get tiles for.
        zoom (int): Zoom level of the tile.
        x (int): X coordinate of the tile.
        y (int): Y coordinate of the tile.
    Returns:
        HttpResponse: Response containing the MVT tile.
    """
    start_time = time.time()
    model = MODEL_BY_TYPE[model_type]
    response = load_tiles(model, x, y, zoom, layer)
    print(f"Request duration: {time.time() - start_time} seconds")
    return response
