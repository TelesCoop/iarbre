from django.conf import settings
from django.contrib.gis.db.models.functions import AsGeoJSON
from django.contrib.gis.gdal import SpatialReference
from gisserver.db import (
    AsEWKT,
    AsGML,
    get_db_geometry_target,
    replace_queryset_geometries,
)
from gisserver.operations import wfs20
from gisserver.output import (
    DBCSVRenderer,
    DBGeoJsonRenderer,
    DBGML32Renderer,
    DBGML32ValueRenderer,
)


def db_precision(crs):
    if SpatialReference(crs.srid).geographic:
        return settings.WFS_GEOGRAPHIC_DB_PRECISION
    return settings.GISSERVER_DB_PRECISION


def gml_kwargs(projection):
    use_modern = not projection.output_crs.force_xy
    return {
        "is_latlon": use_modern and projection.output_crs.is_north_east_order,
        "long_urn": use_modern,
        "precision": db_precision(projection.output_crs),
    }


class GeoJsonRenderer(DBGeoJsonRenderer):
    def decorate_queryset(self, projection, queryset):
        queryset = super(DBGeoJsonRenderer, self).decorate_queryset(
            projection, queryset
        )
        main_geo_element = projection.feature_type.main_geometry_element
        if main_geo_element is None:
            return queryset
        return queryset.defer(main_geo_element.orm_path).annotate(
            _as_db_geojson=AsGeoJSON(
                get_db_geometry_target(main_geo_element, projection.output_crs),
                precision=db_precision(projection.output_crs),
            )
        )


class GML32Renderer(DBGML32Renderer):
    def decorate_queryset(self, projection, queryset):
        queryset = super(DBGML32Renderer, self).decorate_queryset(projection, queryset)
        if projection.has_bounded_by:
            queryset = queryset.annotate(
                _as_envelope_gml=self.get_db_envelope_as_gml(projection, queryset),
            )
        return replace_queryset_geometries(
            queryset,
            projection.geometry_elements,
            projection.output_crs,
            AsGML,
            **gml_kwargs(projection),
        )

    def get_db_envelope_as_gml(self, projection, queryset):
        return AsGML(
            self._get_geometries_union(projection, queryset),
            envelope=True,
            **gml_kwargs(projection),
        )


class GML32ValueRenderer(DBGML32ValueRenderer):
    def decorate_queryset(self, projection, queryset):
        element = projection.property_value_node
        if not element.type.is_geometry:
            return queryset
        return queryset.values(
            "pk",
            gml_member=AsGML(
                get_db_geometry_target(element, projection.output_crs),
                **gml_kwargs(projection),
            ),
        )


class CSVRenderer(DBCSVRenderer):
    def decorate_queryset(self, projection, queryset):
        queryset = super(DBCSVRenderer, self).decorate_queryset(projection, queryset)
        return replace_queryset_geometries(
            queryset,
            projection.geometry_elements,
            projection.output_crs,
            AsEWKT,
            precision=db_precision(projection.output_crs),
        )


RENDERERS = {
    DBGeoJsonRenderer: GeoJsonRenderer,
    DBGML32Renderer: GML32Renderer,
    DBGML32ValueRenderer: GML32ValueRenderer,
    DBCSVRenderer: CSVRenderer,
}


class CrsPrecisionOutputFormatsMixin:
    def get_output_formats(self):
        output_formats = super().get_output_formats()
        for output_format in output_formats:
            output_format.renderer_class = RENDERERS.get(
                output_format.renderer_class, output_format.renderer_class
            )
        return output_formats


class GetFeature(CrsPrecisionOutputFormatsMixin, wfs20.GetFeature):
    pass


class GetPropertyValue(CrsPrecisionOutputFormatsMixin, wfs20.GetPropertyValue):
    pass
