"""Geodata distribution: WFS (django-gisserver), WMS and raw raster downloads."""

import logging
import time
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.core.cache import cache
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from gisserver.crs import CRS, CRS84, WEB_MERCATOR, WGS84
from gisserver.features import FeatureField, FeatureType, ServiceDescription
from gisserver.geometries import WGS84BoundingBox
from gisserver.views import WFSView
from rest_framework.views import APIView

from api.constants import ONE_HOUR, PET_RASTERS, SHADOW_RASTER
from api.schema import NOT_FOUND_RESPONSE, TAG_GEOSERVICES, binary_response
from api.services.rasters import render_grayscale_png
from api.services.wms import discover_layers, layer_bounds_wgs84
from api.utils.wfs_renderers import GetFeature, GetPropertyValue
from iarbre_data.models import BiosphereFunctionalIntegrity, Tile, Vegestrate
from iarbre_data.settings import SRID_DB

logger = logging.getLogger(__name__)
# Named logger, configured in settings.LOGGING.
wfs_logger = logging.getLogger("wfs")


# --- WFS ----------------------------------------------------------------------


def _parse_bbox(bbox_str):
    """Parse a WFS BBOX param into (Polygon, srid).

    Accepts: "minx,miny,maxx,maxy[,CRS_string]"
    SRID is inferred from the optional CRS token or from coordinate magnitude.
    Returns (None, None) on any parse failure.
    """
    if not bbox_str:
        return None, None
    parts = bbox_str.split(",")
    if len(parts) < 4:
        return None, None
    try:
        minx, miny, maxx, maxy = (float(p) for p in parts[:4])
    except ValueError:
        return None, None

    if len(parts) > 4:
        crs_token = parts[4]
        if "2154" in crs_token:
            srid = 2154
        elif "3857" in crs_token:
            srid = 3857
        else:
            srid = 4326
    elif abs(minx) > 180 or abs(maxx) > 180:
        srid = 2154
    else:
        srid = 4326

    poly = Polygon.from_bbox((minx, miny, maxx, maxy))
    poly.srid = srid
    return poly, srid


def _count_features(typename, bbox_poly):
    """Return approximate feature count for the given BBOX using a fast bbox-overlap index scan."""
    if bbox_poly is None:
        return None
    name = typename.lower()
    try:
        if "vegestrate" in name:
            return Vegestrate.objects.filter(geometry__bboverlaps=bbox_poly).count()
        if "biosphere" in name:
            return BiosphereFunctionalIntegrity.objects.filter(
                geometry__bboverlaps=bbox_poly
            ).count()
        return Tile.objects.filter(geometry__bboverlaps=bbox_poly).count()
    except Exception:
        return None


LAMBERT93 = CRS.from_string(f"urn:ogc:def:crs:EPSG::{SRID_DB}")


class TileFeatureType(FeatureType):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            other_crs=[LAMBERT93, WEB_MERCATOR, CRS84, WGS84],
            show_name_field=False,
            **kwargs,
        )

    def get_bounding_box(self):
        return WGS84BoundingBox(4.6, 45.5, 5.2, 46.0)


_tile_qs = Tile.objects.select_related("city").only(
    "geometry",
    "plantability_indice",
    "plantability_normalized_indice",
    "city__code",
    "city__name",
)

_vegestrate_qs = Vegestrate.objects.only("geometry", "strate", "surface")

_biosphere_functional_integrity_qs = BiosphereFunctionalIntegrity.objects.only(
    "geometry", "indice"
)


class IArbreWFSView(WFSView):
    accept_operations = {
        "WFS": {
            **WFSView.accept_operations["WFS"],
            "GetFeature": GetFeature,
            "GetPropertyValue": GetPropertyValue,
        }
    }
    xml_namespace = "http://carte.iarbre.fr/api/wfs"
    xml_namespace_aliases = {"iarbre": "http://carte.iarbre.fr/api/wfs"}

    service_description = ServiceDescription(
        title="IArbre WFS",
        abstract="WFS stream to download IArbre data",
        keywords=["django-gisserver"],
        provider_name="IArbre",
        provider_site="https://iarbre.fr/",
        contact_person="contact@telescoop.fr",
    )

    def dispatch(self, request, *args, **kwargs):
        params = {k.upper(): v for k, v in request.GET.items()}
        req = params.get("REQUEST", "").upper()
        self.city_code = params.get("CITY_CODE")

        if req == "GETTYPES":
            types = [
                {"name": f"iarbre:{ft.name}", "title": ft.title or ft.name}
                for ft in self.get_feature_types()
            ]
            return JsonResponse(types, safe=False)

        if req != "GETFEATURE":
            return super().dispatch(request, *args, **kwargs)

        typename = params.get("TYPENAMES") or params.get("TYPENAME", "unknown")
        count_param = params.get("COUNT", "default")
        start_index = params.get("STARTINDEX", "0")
        output_format = params.get("OUTPUTFORMAT", "gml")
        bbox_str = params.get("BBOX", "")

        bbox_poly, srid = _parse_bbox(bbox_str)
        bbox_area = None
        if bbox_poly:
            ext = bbox_poly.extent
            bbox_area = abs((ext[2] - ext[0]) * (ext[3] - ext[1]))

        feature_count = _count_features(typename, bbox_poly)

        wfs_logger.info(
            "START typename=%s count_param=%s startindex=%s format=%s "
            "bbox_srid=%s bbox_area=%.2f feature_count=%s",
            typename,
            count_param,
            start_index,
            output_format,
            srid,
            bbox_area or 0.0,
            feature_count,
        )

        t_start = time.monotonic()
        response = super().dispatch(request, *args, **kwargs)

        if hasattr(response, "streaming_content"):
            original_content = response.streaming_content
            t_ref = t_start

            def timed_stream():
                yield from original_content
                wfs_logger.info(
                    "END typename=%s elapsed=%.3fs",
                    typename,
                    time.monotonic() - t_ref,
                )

            response.streaming_content = timed_stream()

        return response

    def get_feature_types(self):
        tile_qs = (
            _tile_qs.filter(city__code=self.city_code) if self.city_code else _tile_qs
        )
        return [
            TileFeatureType(
                tile_qs,
                name="plantability",
                title="Plantabilité",
                fields=[
                    "geometry",
                    "plantability_indice",
                    "plantability_normalized_indice",
                    FeatureField("city_code", model_attribute="city.code"),
                    FeatureField("city_name", model_attribute="city.name"),
                ],
            ),
            TileFeatureType(
                _vegestrate_qs,
                name="vegestrate",
                title="Végéstrate",
                fields=["geometry", "strate", "surface"],
            ),
            TileFeatureType(
                _biosphere_functional_integrity_qs,
                name="biosphere_functional_integrity",
                title="Intégrité fonctionnelle de la biosphère",
                fields=["geometry", "indice"],
            ),
        ]


# --- WMS ----------------------------------------------------------------------


_XLINK = "http://www.w3.org/1999/xlink"
_SUPPORTED_CRS = ("EPSG:4326", "EPSG:3857", "EPSG:2154")
_CAPABILITIES_CACHE_TTL = ONE_HOUR
_MAX_SIZE = 4096


@extend_schema(
    tags=[TAG_GEOSERVICES],
    summary="Flux WMS",
    description=(
        "Flux OGC WMS 1.1.1 / 1.3.0 sur les rasters. Ordre des axes du `BBOX` : en "
        "WMS 1.3.0 avec EPSG:4326, `min_lat,min_lon,max_lat,max_lon` ; sinon "
        "`ouest,sud,est,nord`. Erreurs en texte brut."
    ),
    parameters=[
        OpenApiParameter("SERVICE", str, enum=["WMS"]),
        OpenApiParameter("VERSION", str, enum=["1.1.1", "1.3.0"], default="1.3.0"),
        OpenApiParameter(
            "REQUEST",
            str,
            required=True,
            enum=["GetCapabilities", "GetMap", "GetLayers"],
        ),
        OpenApiParameter("LAYERS", str, description="GetMap, ex. `iarbre:lcz`"),
        OpenApiParameter("BBOX", str, description="GetMap, 4 valeurs séparées par `,`"),
        OpenApiParameter("CRS", str, enum=list(_SUPPORTED_CRS), description="1.3.0"),
        OpenApiParameter("SRS", str, enum=list(_SUPPORTED_CRS), description="1.1.1"),
        OpenApiParameter("WIDTH", int, description=f"GetMap, {_MAX_SIZE} maximum"),
        OpenApiParameter("HEIGHT", int, description=f"GetMap, {_MAX_SIZE} maximum"),
        OpenApiParameter("FORMAT", str, enum=["image/png"]),
    ],
    responses={
        (200, "text/xml"): OpenApiResponse(
            OpenApiTypes.STR, description="GetCapabilities (cache 1 heure)"
        ),
        **binary_response("image/png", "GetMap"),
        (200, "application/json"): OpenApiResponse(
            OpenApiTypes.OBJECT,
            description='GetLayers : `[{"name": "iarbre:lcz", "title": "lcz"}]`',
        ),
        (400, "text/plain"): OpenApiResponse(
            OpenApiTypes.STR, description="Requête invalide"
        ),
    },
)
class IArbreWMSView(APIView):
    """OGC WMS 1.1.1 / 1.3.0 endpoint serving raster layers.

    Supported requests:
        GET /api/wms/?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities
        GET /api/wms/?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap
            &LAYERS=iarbre:lcz
            &BBOX=45.5,4.7,46.0,5.2&CRS=EPSG:4326
            &WIDTH=800&HEIGHT=600&FORMAT=image/png

    Axis order for GetMap BBOX:
        WMS 1.3.0 + EPSG:4326 -> lat/lon (min_lat, min_lon, max_lat, max_lon)
        All other CRS or WMS 1.1.1  -> lon/lat (west, south, east, north)
    """

    def get(self, request):
        req_type = request.query_params.get("REQUEST", "").upper()
        version = request.query_params.get("VERSION", "1.3.0")

        if req_type == "GETCAPABILITIES":
            return self._get_capabilities(request, version)
        if req_type == "GETMAP":
            return self._get_map(request, version)
        if req_type == "GETLAYERS":
            return self._get_layers()
        return HttpResponse(
            "Unsupported REQUEST. Use GetCapabilities, GetMap or GetLayers.",
            status=400,
            content_type="text/plain",
        )

    def _get_layers(self):
        return JsonResponse(
            [
                {"name": name, "title": meta["title"]}
                for name, meta in discover_layers().items()
            ],
            safe=False,
        )

    def _get_capabilities(self, request, version):
        # Advertise the URL the client actually called, so the view works
        # under any mount point or alias. The URL is baked into the XML,
        # hence part of the cache key.
        base_url = request.build_absolute_uri(request.path)
        cache_key = f"wms:capabilities:{version}:{base_url}"
        cached = cache.get(cache_key)
        if cached is not None:
            return HttpResponse(cached, content_type="text/xml; charset=utf-8")

        is_130 = version == "1.3.0"
        crs_tag = "CRS" if is_130 else "SRS"

        root = Element("WMS_Capabilities" if is_130 else "WMT_MS_Capabilities")
        root.set("version", version)
        if is_130:
            root.set("xmlns", "http://www.opengis.net/wms")
            root.set("xmlns:xlink", _XLINK)

        service = SubElement(root, "Service")
        SubElement(service, "Name").text = "WMS"
        SubElement(service, "Title").text = "IA·rbre WMS"
        SubElement(
            service, "Abstract"
        ).text = "Service WMS pour les données de végéstrate de la Métropole de Lyon."
        if is_130:
            SubElement(service, "MaxWidth").text = str(_MAX_SIZE)
            SubElement(service, "MaxHeight").text = str(_MAX_SIZE)

        capability = SubElement(root, "Capability")
        req_elem = SubElement(capability, "Request")

        for op_name, fmt in (("GetCapabilities", "text/xml"), ("GetMap", "image/png")):
            op = SubElement(req_elem, op_name)
            SubElement(op, "Format").text = fmt
            or_elem = SubElement(
                SubElement(SubElement(SubElement(op, "DCPType"), "HTTP"), "Get"),
                "OnlineResource",
            )
            or_elem.set(f"{{{_XLINK}}}type", "simple")
            or_elem.set(f"{{{_XLINK}}}href", base_url)

        SubElement(SubElement(capability, "Exception"), "Format").text = "text/plain"

        root_layer = SubElement(capability, "Layer")
        SubElement(root_layer, "Title").text = "IA·rbre"
        for crs in _SUPPORTED_CRS:
            SubElement(root_layer, crs_tag).text = crs

        for name, meta in discover_layers().items():
            layer = SubElement(root_layer, "Layer")
            layer.set("queryable", "0")
            SubElement(layer, "Name").text = name
            SubElement(layer, "Title").text = meta["title"]
            for crs in _SUPPORTED_CRS:
                SubElement(layer, crs_tag).text = crs

            raster_path = meta["path"]
            if not raster_path.exists():
                continue

            west, south, east, north = layer_bounds_wgs84(name, raster_path)

            if is_130:
                geo_bb = SubElement(layer, "EX_GeographicBoundingBox")
                SubElement(geo_bb, "westBoundLongitude").text = f"{west:.6f}"
                SubElement(geo_bb, "eastBoundLongitude").text = f"{east:.6f}"
                SubElement(geo_bb, "southBoundLatitude").text = f"{south:.6f}"
                SubElement(geo_bb, "northBoundLatitude").text = f"{north:.6f}"
                bb = SubElement(layer, "BoundingBox")
                bb.set("CRS", "EPSG:4326")
                bb.set("minx", f"{south:.6f}")
                bb.set("miny", f"{west:.6f}")
                bb.set("maxx", f"{north:.6f}")
                bb.set("maxy", f"{east:.6f}")
            else:
                ll_bb = SubElement(layer, "LatLonBoundingBox")
                ll_bb.set("minx", f"{west:.6f}")
                ll_bb.set("miny", f"{south:.6f}")
                ll_bb.set("maxx", f"{east:.6f}")
                ll_bb.set("maxy", f"{north:.6f}")
                bb = SubElement(layer, "BoundingBox")
                bb.set("SRS", "EPSG:4326")
                bb.set("minx", f"{west:.6f}")
                bb.set("miny", f"{south:.6f}")
                bb.set("maxx", f"{east:.6f}")
                bb.set("maxy", f"{north:.6f}")

        xml_bytes = b'<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(
            root, encoding="unicode"
        ).encode("utf-8")
        cache.set(cache_key, xml_bytes, timeout=_CAPABILITIES_CACHE_TTL)
        return HttpResponse(xml_bytes, content_type="text/xml; charset=utf-8")

    def _get_map(self, request, version):
        params = request.query_params
        layer_name = params.get("LAYERS", "")
        layers = discover_layers()
        layer = layers.get(layer_name)
        if not layer:
            return HttpResponse(
                f"Unknown layer: {layer_name}. Available: {', '.join(layers)}",
                status=400,
                content_type="text/plain",
            )

        fmt = params.get("FORMAT", "image/png")
        if fmt != "image/png":
            return HttpResponse(
                f"Unsupported FORMAT '{fmt}'. Supported: image/png",
                status=400,
                content_type="text/plain",
            )

        crs = params.get("CRS" if version == "1.3.0" else "SRS", "EPSG:4326")

        try:
            bbox_vals = [float(v) for v in params.get("BBOX", "").split(",")]
            if len(bbox_vals) != 4:
                raise ValueError
        except ValueError:
            return HttpResponse("Invalid BBOX", status=400, content_type="text/plain")

        try:
            width, height = self._parse_size(params)
        except ValueError as exc:
            return HttpResponse(str(exc), status=400, content_type="text/plain")

        if version == "1.3.0" and crs == "EPSG:4326":
            min_lat, min_lon, max_lat, max_lon = bbox_vals
            west, south, east, north = min_lon, min_lat, max_lon, max_lat
        else:
            west, south, east, north = bbox_vals

        raster_path = layer["path"]
        if not raster_path.exists():
            return HttpResponse(
                "Raster file not found", status=404, content_type="text/plain"
            )

        try:
            png = render_grayscale_png(
                raster_path, crs, (west, south, east, north), width, height
            )
        except Exception:
            logger.exception("Error generating WMS GetMap for layer %s", layer_name)
            return HttpResponse(
                "Rendering error", status=500, content_type="text/plain"
            )
        return HttpResponse(png, content_type="image/png")

    @staticmethod
    def _parse_size(params) -> tuple[int, int]:
        try:
            width = int(params.get("WIDTH", 256))
            height = int(params.get("HEIGHT", 256))
        except ValueError:
            raise ValueError("Invalid WIDTH or HEIGHT") from None
        if not (0 < width <= _MAX_SIZE and 0 < height <= _MAX_SIZE):
            raise ValueError(f"WIDTH and HEIGHT must be between 1 and {_MAX_SIZE}")
        return width, height


# --- Raster downloads -------------------------------------------------------


def _entry(path: str, filename: str | None = None) -> tuple[str, str]:
    """Build a ``(path, filename)`` tuple, defaulting filename to basename."""
    return path, filename or Path(path).name


base_dir = "rasters/WMS/"
RASTER_MAP: dict[str, tuple[str, str]] = {
    "plantability": _entry(base_dir + "plantability.tif"),
    "plantability_colors": _entry("rasters/plantability_colors.tif"),
    "vegestrate": _entry(base_dir + "vegestrate_02_2023.tif"),
    "vegestrate_ndsm": _entry(base_dir + "vegestrate_02_2023_elevation.tif"),
    "vulnerability": _entry(base_dir + "vulnerability.tif"),
    "vulnerability_colors": _entry(base_dir + "vulnerability_colors.tif"),
    "lcz": _entry(base_dir + "lcz.tif"),
    "lcz_colors": _entry(base_dir + "lcz_colors.tif"),
    **{
        f"pet_{year}": _entry(f"{base_dir}{name}.tif")
        for year, name in PET_RASTERS.items()
    },
    "shadow": _entry(f"{base_dir}{SHADOW_RASTER}.tif"),
}


class FileDownloadView(APIView):
    """Base view for serving pre-generated static files from MEDIA_ROOT.

    Subclasses set ``file_map`` and ``download_content_type`` to configure
    which files are available and how they are served.
    """

    file_map: dict[str, tuple[str, str]] = {}
    download_content_type: str = "application/octet-stream"

    def get(self, request, file_key: str):
        if file_key not in self.file_map:
            available = ", ".join(self.file_map)
            raise Http404(f"Unknown key '{file_key}'. Available: {available}.")

        relative_path, filename = self.file_map[file_key]
        full_path = Path(settings.MEDIA_ROOT) / relative_path

        if not full_path.exists():
            raise Http404(f"File not found: {filename}.")

        response = FileResponse(
            full_path.open("rb"),
            content_type=self.download_content_type,
            as_attachment=True,
            filename=filename,
        )
        response["Cache-Control"] = f"public, max-age={ONE_HOUR}"
        return response


@extend_schema(
    tags=[TAG_GEOSERVICES],
    summary="Téléchargement d'un raster GeoTIFF",
    parameters=[
        OpenApiParameter(
            "raster_type", str, OpenApiParameter.PATH, enum=list(RASTER_MAP)
        )
    ],
    responses={
        **binary_response("image/tiff", "GeoTIFF en pièce jointe"),
        404: NOT_FOUND_RESPONSE,
    },
)
class RasterDownloadView(FileDownloadView):
    """Download raster files (GeoTIFF). Example: ``GET /api/rasters/plantability/``."""

    file_map = RASTER_MAP
    download_content_type = "image/tiff"

    def get(self, request, raster_type: str):
        return super().get(request, raster_type)
