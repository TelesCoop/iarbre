from django.urls import path, include
from rest_framework import routers

from .views import FeedbackView, TileView

router = routers.DefaultRouter()

urlpatterns = [
    path(
        "tiles/<geolevel>/<datatype>/<zoom>/<x>/<y>.mvt",
        TileView.as_view(),
        name="retrieve-tile",
    ),
    path("feedback/", FeedbackView.as_view(), name="create-feedback"),
    path("", include(router.urls)),
]
