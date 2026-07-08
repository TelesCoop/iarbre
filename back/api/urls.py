from django.urls import path, include
from rest_framework import routers

from .views.tile_views import TileDetailsView, ScoresInPolygonView
from .views.dashboard_views import DashboardView, DashboardPolygonView
from .views.export_views import DashboardPdfExportView
from .views import (
    CityView,
    IrisView,
    FeedbackView,
    TileView,
    HealthCheckView,
    QPVListView,
    CityBoundaryView,
    MetadataView,
    RasterDownloadView,
    IArbreWFSView,
    IArbreWMSView,
    OrthophotoTileView,
    BiosphereLandCoverAtPointView,
    VegetationHeightTileView,
    VegetationHeightAtPointView,
)

router = routers.DefaultRouter()
router.register(r"cities", CityView, basename="city")
router.register(r"iris", IrisView, basename="iris")

urlpatterns = [
    path(
        "tiles/<geolevel>/<datatype>/<zoom>/<x>/<y>.mvt",
        TileView.as_view(),
        name="retrieve-tile",
    ),
    # Specific URLs BEFORE general catch-alls with path parameters
    path(
        "tiles/<datatype>/in-polygon/",
        ScoresInPolygonView.as_view(),
        name="scores-in-polygon",
    ),
    path(
        "tiles/vegetation-height/value/",
        VegetationHeightAtPointView.as_view(),
        name="vegetation-height-at-point",
    ),
    path(
        "tiles/vegetation-height/<int:z>/<int:x>/<int:y>.png",
        VegetationHeightTileView.as_view(),
        name="vegetation-height-tile",
    ),
    path(
        "tiles/<datatype>/<id>/",
        TileDetailsView.as_view(),
        name="retrieve-tile-details",
    ),
    path("feedback/", FeedbackView.as_view(), name="create-feedback"),
    path("qpv/", QPVListView.as_view(), name="qpv-list"),
    path("boundaries/cities/", CityBoundaryView.as_view(), name="city-boundaries"),
    path(
        "rasters/<str:raster_type>/",
        RasterDownloadView.as_view(),
        name="download-raster",
    ),
    path(
        "dashboard/in-polygon/",
        DashboardPolygonView.as_view(),
        name="dashboard-in-polygon",
    ),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path(
        "dashboard/export-pdf/",
        DashboardPdfExportView.as_view(),
        name="dashboard-export-pdf",
    ),
    path("", include(router.urls)),
    path("health-check/", HealthCheckView.as_view(), name="health-check"),
    path("metadata/", MetadataView.as_view()),
    path("wfs/", IArbreWFSView.as_view()),
    path("wms/", IArbreWMSView.as_view()),
    path(
        "orthophoto/<int:z>/<int:x>/<int:y>.png",
        OrthophotoTileView.as_view(),
        name="orthophoto-tile",
    ),
    path(
        "biosphere/land-cover-at-point/",
        BiosphereLandCoverAtPointView.as_view(),
        name="biosphere-land-cover-at-point",
    ),
]
