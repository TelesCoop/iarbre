"""Map tiles served by z/x/y: vector (MVT) and raster (PNG)."""

import logging
from pathlib import Path

import mercantile
import numpy as np
import requests
from django.conf import settings
from django.http import Http404, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from PIL import Image
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from api.constants import ONE_DAY, ONE_MONTH, PET_RASTERS, SHADOW_RASTER, GeoLevel
from api.schema import NOT_FOUND_RESPONSE, TAG_MAP_LAYERS, binary_response
from api.services.rasters import (
    TILE_SIZE,
    WMS_RASTER_DIR,
    colorize,
    empty_png,
    encode_terrarium,
    png_bytes,
    read_tile,
    vegetation_height_raster,
)
from iarbre_data.models import MVTTile
from iarbre_data.utils.hourly_rasters import hour_raster_path
from iarbre_data.utils.palettes import VEGESTRATE_COLOR_MAP

logger = logging.getLogger(__name__)

HOURS = range(25)

ORTHOPHOTO_WMS_URL = "https://download.data.grandlyon.com/wms/grandlyon"
ORTHOPHOTO_WMS_LAYER = "grandlyon:ortho_latest"
ORTHOPHOTO_WMS_TIMEOUT = 10
ORTHOPHOTO_CACHE_DURATION = 6 * ONE_MONTH


def _png_response(content: bytes) -> HttpResponse:
    return HttpResponse(content, content_type="image/png")


def _int_param(request, name: str, allowed) -> int:
    try:
        value = int(request.query_params.get(name, ""))
    except ValueError:
        value = None
    if value not in allowed:
        raise ValidationError({name: f"Must be one of {', '.join(map(str, allowed))}."})
    return value


# --- Vector tiles ---------------------------------------------------------------


MVT_DATATYPES = [
    "plantability",
    "vegestrate",
    "lcz",
    "vulnerability",
    "cadastre",
    "biosphere_functional_integrity",
]

_XYZ_PARAMETERS = [
    OpenApiParameter(name, OpenApiTypes.INT, OpenApiParameter.PATH)
    for name in ("x", "y")
]


@extend_schema_view(get=extend_schema(operation_id="mvt_tile"))
@extend_schema(
    tags=[TAG_MAP_LAYERS],
    summary="Tuile vectorielle (MVT)",
    description=(
        "Tuiles Mapbox Vector Tile pré-générées, EPSG:3857. Le nom de la couche "
        "est `{geolevel}--{datatype}`. Cache : 24 heures."
    ),
    parameters=[
        OpenApiParameter("geolevel", str, OpenApiParameter.PATH, enum=GeoLevel.values),
        OpenApiParameter("datatype", str, OpenApiParameter.PATH, enum=MVT_DATATYPES),
        OpenApiParameter("zoom", OpenApiTypes.INT, OpenApiParameter.PATH),
        *_XYZ_PARAMETERS,
    ],
    responses={
        **binary_response("application/x-protobuf", "Tuile MVT"),
        404: NOT_FOUND_RESPONSE,
    },
)
class TileView(generics.RetrieveAPIView):
    def get_object(self):
        return MVTTile.objects.get(
            geolevel=self.kwargs.get("geolevel"),
            datatype=self.kwargs.get("datatype"),
            zoom_level=self.kwargs.get("zoom"),
            tile_x=self.kwargs.get("x"),
            tile_y=self.kwargs.get("y"),
        )

    @method_decorator(cache_page(ONE_DAY))
    def get(self, request, *args, **kwargs):
        try:
            return HttpResponse(
                self.get_object().mvt_file, content_type="application/x-protobuf"
            )
        except MVTTile.DoesNotExist:
            logger.warning("MVTTile not found: %s", self.kwargs)
            raise Http404


# --- Raster tiles from local GeoTIFFs -------------------------------------------


class RasterTileView(APIView):
    """Base view serving a GeoTIFF as {z}/{x}/{y} PNG tiles.

    Subclasses pick the raster (``raster_path``) and turn the raw band into
    RGBA pixels (``render``), typically with ``api.services.rasters.colorize``
    or ``encode_terrarium``.
    """

    def raster_path(self, request) -> Path:
        raise NotImplementedError

    def render(self, data: np.ndarray, nodata, request) -> np.ndarray:
        raise NotImplementedError

    @method_decorator(cache_page(ONE_DAY))
    def get(self, request, z, x, y):
        raster_path = self.raster_path(request)
        if not raster_path.exists():
            raise Http404("Raster file not found")

        try:
            data, nodata = read_tile(
                raster_path, mercantile.Tile(int(x), int(y), int(z))
            )
            if data is None:
                return _png_response(empty_png())
            rgba_data = self.render(data, nodata, request)
        except Exception:
            logger.exception("Error generating raster tile %s/%s/%s", z, x, y)
            return _png_response(empty_png())

        return _png_response(png_bytes(Image.fromarray(rgba_data, mode="RGBA")))


@extend_schema_view(get=extend_schema(operation_id="vegetation_height_tile"))
@extend_schema(
    tags=[TAG_MAP_LAYERS],
    summary="Tuile raster de hauteur de végétation",
    description="Tuiles PNG 256×256 générées à la volée. Cache : 24 heures.",
    parameters=[
        OpenApiParameter(
            "kind",
            str,
            enum=["class", "raw"],
            default="class",
            description=(
                "`class` : pixels colorés par classe. `raw` : hauteur encodée en "
                "Terrarium (`R * 256 + G + B / 256 - 32768`)."
            ),
        )
    ],
    responses={**binary_response("image/png", "Tuile PNG"), 404: NOT_FOUND_RESPONSE},
)
class VegetationHeightTileView(RasterTileView):
    """
    Serve vegetation raster data as {z}/{x}/{y} PNG tiles for MapLibre.
    Converts GeoTIFF to PNG tiles on-the-fly with proper georeferencing.
    """

    def raster_path(self, request) -> Path:
        return vegetation_height_raster()

    def render(self, data, nodata, request):
        if request.query_params.get("kind", "class") == "raw":
            return encode_terrarium(data, nodata)
        return colorize(data, VEGESTRATE_COLOR_MAP)


class HourlyRasterTileView(RasterTileView):
    def raster_name(self, request) -> str:
        raise NotImplementedError

    def raster_path(self, request) -> Path:
        hour = _int_param(request, "hour", HOURS)
        source = (
            Path(settings.MEDIA_ROOT)
            / WMS_RASTER_DIR
            / f"{self.raster_name(request)}.tif"
        )
        return hour_raster_path(source, hour)

    def render(self, data, nodata, request):
        return encode_terrarium(data, nodata)


class PetTileView(HourlyRasterTileView):
    def raster_name(self, request) -> str:
        return PET_RASTERS[_int_param(request, "year", list(PET_RASTERS))]


class ShadowTileView(HourlyRasterTileView):
    def raster_name(self, request) -> str:
        return SHADOW_RASTER


# --- Orthophoto proxied from Grand Lyon --------------------------------------------


class OrthophotoTileView(APIView):
    """Proxy WMS tiles from Grand Lyon as XYZ PNG tiles.

    Converts XYZ tile coordinates to WMS GetMap requests against
    the Grand Lyon orthophoto WMS service.

    Example: GET /api/orthophoto/14/8345/5765.png
    """

    @method_decorator(cache_page(ORTHOPHOTO_CACHE_DURATION, cache="orthophoto"))
    def get(self, request, z, x, y):
        z, x, y = int(z), int(x), int(y)

        bbox = mercantile.xy_bounds(mercantile.Tile(x, y, z))

        params = {
            "SERVICE": "WMS",
            "VERSION": "1.3.0",
            "REQUEST": "GetMap",
            "LAYERS": ORTHOPHOTO_WMS_LAYER,
            "CRS": "EPSG:3857",
            "BBOX": f"{bbox.left},{bbox.bottom},{bbox.right},{bbox.top}",
            "WIDTH": TILE_SIZE,
            "HEIGHT": TILE_SIZE,
            "FORMAT": "image/png",
            "TRANSPARENT": "TRUE",
        }

        try:
            wms_response = requests.get(
                ORTHOPHOTO_WMS_URL, params=params, timeout=ORTHOPHOTO_WMS_TIMEOUT
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
        response["Cache-Control"] = f"public, max-age={ORTHOPHOTO_CACHE_DURATION}"
        return response
