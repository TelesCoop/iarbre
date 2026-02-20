from django.urls import path, include
from rest_framework import routers

from .views.tile_views import TileDetailsView, ScoresInPolygonView
from .views.dashboard_views import DashboardView
from .views import (
    CityView,
    IrisView,
    FeedbackView,
    TileView,
    HealthCheckView,
    QPVListView,
    MetadataView,
    RasterDownloadView,
    VegetationTileView,
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
    # Specific URL should be BEFORE general URL with <id>
    path(
        "tiles/<datatype>/in-polygon/",
        ScoresInPolygonView.as_view(),
        name="scores-in-polygon",
    ),
    path(
        "tiles/vegetation/<int:z>/<int:x>/<int:y>.png",
        VegetationTileView.as_view(),
        name="retrieve-vegetation-tile",
    ),
    path(
        "tiles/<datatype>/<id>/",
        TileDetailsView.as_view(),
        name="retrieve-tile-details",
    ),
    path("feedback/", FeedbackView.as_view(), name="create-feedback"),
    path("qpv/", QPVListView.as_view(), name="qpv-list"),
    path(
        "rasters/<str:raster_type>/",
        RasterDownloadView.as_view(),
        name="download-raster",
    ),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("", include(router.urls)),
    path("health-check/", HealthCheckView.as_view(), name="health-check"),
    path("metadata/", MetadataView.as_view()),
]
