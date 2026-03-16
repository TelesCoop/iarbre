from django.contrib.gis.db.models.functions import SnapToGrid
from gisserver.crs import CRS84, WEB_MERCATOR, CRS
from gisserver.features import FeatureField, FeatureType, ServiceDescription
from gisserver.geometries import WGS84BoundingBox
from gisserver.views import WFSView
from iarbre_data.models import Tile, Vegestrate


class AnnotationGeometryField(FeatureField):
    """FeatureField that reads geometry from a queryset annotation.

    django-gisserver's bind() validates model_attribute against model._meta,
    which rejects annotation names. This subclass bypasses that check by
    resolving model_field from self.name (the real geometry field) while
    keeping model_attribute pointing at the annotation for value access.
    """

    def bind(self, model, parent=None, feature_type=None):
        if self.model is not None:
            raise RuntimeError(f"Feature field '{self.name}' cannot be reused")
        self.model = model
        self.parent = parent
        self.feature_type = feature_type
        self.model_field = model._meta.get_field(self.name)


class TileFeatureType(FeatureType):
    def get_bounding_box(self):
        return WGS84BoundingBox(4.6, 45.5, 5.2, 46.0)


LAMBERT93 = CRS.from_string("urn:ogc:def:crs:EPSG::2154")

_tile_qs = Tile.objects.only(
    "plantability_indice", "plantability_normalized_indice"
).annotate(snapped_geom=SnapToGrid("geometry", 0.1))

_vegestrate_qs = Vegestrate.objects.only("strate", "surface").annotate(
    snapped_geom=SnapToGrid("geometry", 0.1)
)


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
                    AnnotationGeometryField("geometry", model_attribute="snapped_geom"),
                    "plantability_indice",
                    "plantability_normalized_indice",
                ],
                geometry_field_name="snapped_geom",
                other_crs=[LAMBERT93, CRS84, WEB_MERCATOR],
            ),
            TileFeatureType(
                _vegestrate_qs,
                fields=[
                    AnnotationGeometryField("geometry", model_attribute="snapped_geom"),
                    "strate",
                    "surface",
                ],
                geometry_field_name="snapped_geom",
                other_crs=[LAMBERT93, CRS84, WEB_MERCATOR],
            ),
        ]
