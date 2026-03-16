from gisserver.crs import CRS84, WEB_MERCATOR, CRS
from gisserver.features import FeatureType, ServiceDescription
from gisserver.geometries import WGS84BoundingBox
from gisserver.views import WFSView
from iarbre_data.models import Tile, Vegestrate


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
