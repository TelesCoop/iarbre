import io
import logging
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

import numpy as np
import rasterio
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from PIL import Image
from pyproj import Transformer
from rasterio.warp import Resampling
from rasterio.windows import from_bounds
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

_XLINK = "http://www.w3.org/1999/xlink"
_SUPPORTED_CRS = ("EPSG:4326", "EPSG:3857", "EPSG:2154")
_CAPABILITIES_CACHE_TTL = 60 * 60
_WMS_RASTER_DIR = "rasters/WMS"


def _discover_layers() -> dict:
    """Discover the available WMS layers by globbing ``media/rasters/WMS/*.tif``.

    Each ``<name>.tif`` becomes the layer ``iarbre:<name>``. The layer list is
    driven by what is on disk, not by a static registry.
    """
    wms_root = Path(settings.MEDIA_ROOT) / _WMS_RASTER_DIR
    if not wms_root.is_dir():
        return {}
    return {
        f"iarbre:{tif.stem}": {"title": tif.stem, "path": tif}
        for tif in sorted(wms_root.glob("*.tif"))
    }


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
                for name, meta in _discover_layers().items()
            ],
            safe=False,
        )

    def _get_capabilities(self, request, version):
        cache_key = f"wms:capabilities:{version}"
        cached = cache.get(cache_key)
        if cached is not None:
            return HttpResponse(cached, content_type="text/xml; charset=utf-8")

        base_url = request.build_absolute_uri("/api/wms/")
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

        for name, meta in _discover_layers().items():
            layer = SubElement(root_layer, "Layer")
            layer.set("queryable", "0")
            SubElement(layer, "Name").text = name
            SubElement(layer, "Title").text = meta["title"]
            for crs in _SUPPORTED_CRS:
                SubElement(layer, crs_tag).text = crs

            raster_path = meta["path"]
            if not raster_path.exists():
                continue

            bounds_key = f"wms:bounds:{name}"
            bounds = cache.get(bounds_key)
            if bounds is None:
                with rasterio.open(raster_path) as src:
                    t = Transformer.from_crs(src.crs, "EPSG:4326", always_xy=True)
                    west, south = t.transform(src.bounds.left, src.bounds.bottom)
                    east, north = t.transform(src.bounds.right, src.bounds.top)
                bounds = (west, south, east, north)
                cache.set(bounds_key, bounds, timeout=None)
            west, south, east, north = bounds

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
        layers = _discover_layers()
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
            width = int(params.get("WIDTH", 256))
            height = int(params.get("HEIGHT", 256))
        except ValueError:
            return HttpResponse(
                "Invalid WIDTH or HEIGHT", status=400, content_type="text/plain"
            )

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
            return self._render_layer(
                raster_path,
                crs,
                west,
                south,
                east,
                north,
                width,
                height,
            )
        except Exception:
            logger.exception("Error generating WMS GetMap for layer %s", layer_name)
            return HttpResponse(
                "Rendering error", status=500, content_type="text/plain"
            )

    def _render_layer(self, raster_path, crs, west, south, east, north, width, height):
        with rasterio.open(raster_path) as src:
            transformer = Transformer.from_crs(crs, src.crs, always_xy=True)
            left, bottom = transformer.transform(west, south)
            right, top = transformer.transform(east, north)

            b = src.bounds
            if right < b.left or left > b.right or top < b.bottom or bottom > b.top:
                return self._empty_image(width, height)

            window = from_bounds(left, bottom, right, top, transform=src.transform)
            data = src.read(
                1,
                window=window,
                out_shape=(height, width),
                resampling=Resampling.nearest,
            )
            nodata = src.nodata

        img = self._grayscale_image(data, nodata)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return HttpResponse(buf.getvalue(), content_type="image/png")

    @staticmethod
    def _grayscale_image(data: np.ndarray, nodata) -> Image.Image:
        """Encode raw raster values as a grayscale ("LA") PNG, no color mapping.

        Pixel intensity is the raw band value (clipped to 0-255); nodata and NaN
        pixels are made fully transparent so the stream carries no color code.
        """
        arr = np.asarray(data)
        transparent = np.zeros(arr.shape, dtype=bool)
        if np.issubdtype(arr.dtype, np.floating):
            transparent |= np.isnan(arr)
        if nodata is not None:
            transparent |= arr == nodata

        gray = np.clip(np.nan_to_num(arr, nan=0.0), 0, 255).astype(np.uint8)
        alpha = np.where(transparent, 0, 255).astype(np.uint8)
        return Image.fromarray(np.dstack([gray, alpha]), mode="LA")

    def _empty_image(self, width: int, height: int) -> HttpResponse:
        """Return a transparent PNG of the requested dimensions."""
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return HttpResponse(buf.getvalue(), content_type="image/png")
