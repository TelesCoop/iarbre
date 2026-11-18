from django.urls import path, include
from rest_framework import routers

from .views import (
    BiosphereLandCoverAtPointView,
    CityBoundaryView,
    CityView,
    DashboardExportPdfView,
    DashboardExportScopeView,
    DashboardPolygonView,
    DashboardView,
    FeedbackView,
    HealthCheckView,
    IArbreWFSView,
    IArbreWMSView,
    IrisView,
    MetadataView,
    OrthophotoTileView,
    PetTileView,
    PublicBuildingListView,
    QPVListView,
    RasterDownloadView,
    ScoresInPolygonView,
    ShadowTileView,
    ShortLinkCreateView,
    ShortLinkDetailView,
    TileDetailsView,
    TileView,
    VegetationHeightAtPointView,
    VegetationHeightTileView,
)

router = routers.DefaultRouter()
router.register(r"cities", CityView, basename="city")
router.register(r"iris", IrisView, basename="iris")

# Sections follow the modules of ``api.views``. Within ``tiles/``, the fixed
# paths (``value/``, ``in-polygon/``) must stay before ``tiles/<datatype>/<id>/``.
urlpatterns = [
    # --- tiles ----------------------------------------------------------------------
    path(
        "tiles/<geolevel>/<datatype>/<zoom>/<x>/<y>.mvt",
        TileView.as_view(),
        name="retrieve-tile",
    ),
    path(
        "tiles/vegetation-height/<int:z>/<int:x>/<int:y>.png",
        VegetationHeightTileView.as_view(),
        name="vegetation-height-tile",
    ),
    path(
        "tiles/pet/<int:z>/<int:x>/<int:y>.png",
        PetTileView.as_view(),
        name="pet-tile",
    ),
    path(
        "tiles/shadow/<int:z>/<int:x>/<int:y>.png",
        ShadowTileView.as_view(),
        name="shadow-tile",
    ),
    path(
        "orthophoto/<int:z>/<int:x>/<int:y>.png",
        OrthophotoTileView.as_view(),
        name="orthophoto-tile",
    ),
    # --- spatial --------------------------------------------------------------------
    path(
        "tiles/vegetation-height/value/",
        VegetationHeightAtPointView.as_view(),
        name="vegetation-height-at-point",
    ),
    path(
        "tiles/<datatype>/in-polygon/",
        ScoresInPolygonView.as_view(),
        name="scores-in-polygon",
    ),
    path(
        "tiles/<datatype>/<id>/",
        TileDetailsView.as_view(),
        name="retrieve-tile-details",
    ),
    path(
        "biosphere/land-cover-at-point/",
        BiosphereLandCoverAtPointView.as_view(),
        name="biosphere-land-cover-at-point",
    ),
    # --- dashboard ------------------------------------------------------------------
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path(
        "dashboard/in-polygon/",
        DashboardPolygonView.as_view(),
        name="dashboard-in-polygon",
    ),
    path(
        "dashboard/export-scope/<str:token>/",
        DashboardExportScopeView.as_view(),
        name="dashboard-export-scope",
    ),
    path(
        "dashboard/export-pdf/",
        DashboardExportPdfView.as_view(),
        name="dashboard-export-pdf",
    ),
    # --- reference ------------------------------------------------------------------
    path("", include(router.urls)),
    path("boundaries/cities/", CityBoundaryView.as_view(), name="city-boundaries"),
    path("qpv/", QPVListView.as_view(), name="qpv-list"),
    path(
        "public-buildings/",
        PublicBuildingListView.as_view(),
        name="public-buildings-list",
    ),
    # --- geoservices ----------------------------------------------------------------
    path("wfs/", IArbreWFSView.as_view()),
    path("wms/", IArbreWMSView.as_view()),
    path(
        "rasters/<str:raster_type>/",
        RasterDownloadView.as_view(),
        name="download-raster",
    ),
    # --- user -----------------------------------------------------------------------
    path("feedback/", FeedbackView.as_view(), name="create-feedback"),
    path("short-links/", ShortLinkCreateView.as_view(), name="create-short-link"),
    path(
        "short-links/<str:code>/",
        ShortLinkDetailView.as_view(),
        name="retrieve-short-link",
    ),
    # --- system ---------------------------------------------------------------------
    path("health-check/", HealthCheckView.as_view(), name="health-check"),
    path("metadata/", MetadataView.as_view()),
]
