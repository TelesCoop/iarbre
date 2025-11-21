from django.urls import path, include
from rest_framework import routers

from .views.tile_views import TileDetailsView
from .views import (
    CityView,
    IrisView,
    FeedbackView,
    TileView,
    HealthCheckView,
    QPVListView,
    MetadataView,
    RasterDownloadView,
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
    path(
        "tiles/<datatype>/<id>/",
        TileDetailsView.as_view(),
        name="retrieve-tile-details",
    ),
    path("feedback/", FeedbackView.as_view(), name="create-feedback"),
    path("qpv/", QPVListView.as_view(), name="qpv-list"),
    path(
        "rasters/plantability/",
        RasterDownloadView.as_view(),
        name="download-plantability-raster",
    ),
    path("", include(router.urls)),
    path("health-check/", HealthCheckView.as_view(), name="health-check"),
    path("metadata/", MetadataView.as_view()),
]
