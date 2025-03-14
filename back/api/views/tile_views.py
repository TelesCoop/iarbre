import time
from rest_framework.decorators import api_view
from django.views.decorators.cache import cache_page
from api.map import load_tiles


@cache_page(60 * 60 * 24)
@api_view(["GET"])
def retrieve_tiles(request, geolevel: str, datatype: str, zoom: int, x: int, y: int):
    """View to get tiles for a specific model type.

    This view handles GET requests to retrieve tiles for a given model type, zoom level,
    and tile coordinates (x, y).
    Args:
        request (HttpRequest): The HTTP request object.
        geolevel (str): Geolevel to get tiles for.
        datatype (str): Datatype to get tiles for.
        zoom (int): Zoom level of the tile.
        x (int): X coordinate of the tile.
        y (int): Y coordinate of the tile.

    Returns:
        HttpResponse: Response containing the MVT tile.
    """
    start_time = time.time()
    response = load_tiles(geolevel, datatype, x, y, zoom)
    print(f"Request duration: {time.time() - start_time} seconds")
    return response
