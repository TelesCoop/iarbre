import logging

import requests
from django.http import HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from api.utils.tile_math import tile_to_bbox

logger = logging.getLogger(__name__)

WMS_BASE_URL = "https://download.data.grandlyon.com/wms/grandlyon"
WMS_LAYER = "grandlyon:ortho_latest"
TILE_SIZE = 256
# Cache tiles for 30 days (static imagery)
CACHE_DURATION = 60 * 60 * 24 * 30
WMS_TIMEOUT = 10


class OrthophotoTileView(APIView):
    """Proxy WMS tiles from Grand Lyon as XYZ PNG tiles.

    Converts XYZ tile coordinates to WMS GetMap requests against
    the Grand Lyon orthophoto WMS service.

    Example: GET /api/orthophoto/14/8345/5765.png
    """

    @method_decorator(cache_page(CACHE_DURATION))
    def get(self, request, z, x, y):
        z, x, y = int(z), int(x), int(y)

        bbox = tile_to_bbox(z, x, y)

        params = {
            "SERVICE": "WMS",
            "VERSION": "1.3.0",
            "REQUEST": "GetMap",
            "LAYERS": WMS_LAYER,
            "CRS": "EPSG:3857",
            "BBOX": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
            "WIDTH": TILE_SIZE,
            "HEIGHT": TILE_SIZE,
            "FORMAT": "image/png",
            "TRANSPARENT": "TRUE",
        }

        try:
            wms_response = requests.get(
                WMS_BASE_URL, params=params, timeout=WMS_TIMEOUT
            )
            wms_response.raise_for_status()
        except requests.RequestException:
            logger.exception("WMS request failed for tile z=%s x=%s y=%s", z, x, y)
            raise Http404

        content_type = wms_response.headers.get("Content-Type", "image/png")
        if "xml" in content_type or "html" in content_type:
            logger.warning(
                "WMS returned non-image response for tile z=%s x=%s y=%s: %s",
                z,
                x,
                y,
                wms_response.text[:200],
            )
            raise Http404

        response = HttpResponse(wms_response.content, content_type="image/png")
        response["Cache-Control"] = f"public, max-age={CACHE_DURATION}"
        return response
