from django.urls import path, include
from rest_framework import routers

# from api import views
from .views.tile_views import retrieve_tiles
from .views.feedback_views import receive_feedback

router = routers.DefaultRouter()


urlpatterns = [
    path(
        "tiles/<str:geolevel>/<str:datatype>/<int:zoom>/<int:x>/<int:y>.mvt",
        retrieve_tiles,
    ),
    path("feedback/", receive_feedback),
    # # path("feedback/", views.receive_feedback),
    path("", include(router.urls)),
]
