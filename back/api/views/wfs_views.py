import logging
import time

from django.contrib.gis.geos import Polygon
from gisserver.crs import CRS84, WEB_MERCATOR, CRS
from gisserver.features import FeatureType, ServiceDescription
from gisserver.geometries import WGS84BoundingBox
from gisserver.views import WFSView
from iarbre_data.models import Tile, Vegestrate

logger = logging.getLogger("wfs")


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
        return Tile.objects.filter(geometry__bboverlaps=bbox_poly).count()
    except Exception:
        return None


class TileFeatureType(FeatureType):
    def get_bounding_box(self):
        return WGS84BoundingBox(4.6, 45.5, 5.2, 46.0)


LAMBERT93 = CRS.from_string("urn:ogc:def:crs:EPSG::2154")

_tile_qs = Tile.objects.only(
    "geometry",
    "plantability_indice",
    "plantability_normalized_indice",
)

_vegestrate_qs = Vegestrate.objects.only("geometry", "strate", "surface")


class IArbreWFSView(WFSView):
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
        if params.get("REQUEST", "").upper() != "GETFEATURE":
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

        logger.info(
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
                logger.info(
                    "END typename=%s elapsed=%.3fs",
                    typename,
                    time.monotonic() - t_ref,
                )

            response.streaming_content = timed_stream()

        return response

    def get_feature_types(self):
        return [
            TileFeatureType(
                _tile_qs,
                name="plantability",
                fields=[
                    "geometry",
                    "plantability_indice",
                    "plantability_normalized_indice",
                ],
                other_crs=[LAMBERT93, CRS84, WEB_MERCATOR],
            ),
            TileFeatureType(
                _vegestrate_qs,
                fields=["geometry", "strate", "surface"],
                other_crs=[LAMBERT93, CRS84, WEB_MERCATOR],
            ),
        ]
