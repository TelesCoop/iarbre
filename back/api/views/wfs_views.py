from gisserver.crs import CRS84, WEB_MERCATOR, CRS
from gisserver.features import FeatureType, FeatureField, ServiceDescription
from gisserver.geometries import WGS84BoundingBox
from gisserver.views import WFSView
from iarbre_data.models import Tile


class TileFeatureType(FeatureType):
    def get_bounding_box(self):
        return WGS84BoundingBox(4.6, 45.5, 5.2, 46.0)


LAMBERT93 = CRS.from_string("urn:ogc:def:crs:EPSG::2154")


class PlantabilityWFSView(WFSView):
    """WFS view for plantability."""

    xml_namespace = "http://carte.iarbre.fr/gisserver"

    # The service metadata
    service_description = ServiceDescription(
        title="Plantability",
        abstract="WFS stream to download plantability data",
        keywords=["django-gisserver"],
        provider_name="IArbre",
        provider_site="https://www.carte.iarbre.fr/",
        contact_person="contact@telescoop.fr",
    )

    def get_feature_types(self):
        # FeatureField instances cannot be reused across requests, so they must be created fresh here.
        return [
            TileFeatureType(
                Tile.objects.select_related("iris", "city").all(),
                fields=[
                    "geometry",
                    "plantability_indice",
                    "plantability_normalized_indice",
                    "meta_factors",
                    FeatureField("iris_name", model_attribute="iris.name"),
                    FeatureField("city_name", model_attribute="city.name"),
                ],
                other_crs=[LAMBERT93, CRS84, WEB_MERCATOR],
            )
        ]
