import time
from rest_framework import generics
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from iarbre_data.models import MVTTile


class TileView(generics.RetrieveAPIView):
    @method_decorator(cache_page(60 * 60 * 24))
    @action(
        detail=True, methods=["get"], url_path=r"<geolevel>/<datatype>/<zoom>/<x>/<y>"
    )
    def get(request, geolevel: str, datatype: str, zoom: int, x: int, y: int):
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
        tile = MVTTile.objects.get(
            geolevel=geolevel, datatype=datatype, zoom_level=zoom, tile_x=x, tile_y=y
        )

        print(f"Request duration: {time.time() - start_time} seconds")
        return HttpResponse(tile.mvt_file, content_type="application/x-protobuf")
