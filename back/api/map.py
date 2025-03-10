from functools import lru_cache

from django.http import HttpResponse, Http404
from iarbre_data.models import MVTTile


@lru_cache(maxsize=1024)
def load_tiles(geolevel, datatype, x, y, zoom):
    try:
        tile = MVTTile.objects.get(
            geolevel=geolevel, datatype=datatype, zoom_level=zoom, tile_x=x, tile_y=y
        )
        return HttpResponse(tile.mvt_file, content_type="application/x-protobuf")
    except (MVTTile.DoesNotExist, FileNotFoundError):
        raise Http404("Tile not found")
