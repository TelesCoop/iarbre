"""Public API, mounted on ``/api/v1/``.

Stable contract for third parties (and the frontend): documented in
``docs/back/api-rest.md``, open to any origin. Breaking changes need a new version.
"""

from django.urls import path, include
from rest_framework import routers

from api.views import (
    BiosphereLandCoverAtPointView,
    CityBoundaryView,
    CityView,
    DashboardPolygonView,
    DashboardView,
    IArbreWFSView,
    IArbreWMSView,
    IrisView,
    MetadataView,
    PublicBuildingListView,
    QPVListView,
    RasterDownloadView,
    ScoresInPolygonView,
    TileView,
    VegetationHeightAtPointView,
    VegetationHeightTileView,
)

router = routers.DefaultRouter()
router.register(r"cities", CityView, basename="city")
router.register(r"iris", IrisView, basename="iris")

# Sections follow the modules of ``api.views``.
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
    path("wfs/", IArbreWFSView.as_view(), name="wfs"),
    path("wms/", IArbreWMSView.as_view(), name="wms"),
    path(
        "rasters/<str:raster_type>/",
        RasterDownloadView.as_view(),
        name="download-raster",
    ),
    # --- system ---------------------------------------------------------------------
    path("metadata/", MetadataView.as_view(), name="metadata"),
]
