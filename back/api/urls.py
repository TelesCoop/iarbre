from django.urls import path, include
from rest_framework import routers

# from api import views
from api.views.tiles_view import TileView

router = routers.DefaultRouter()


router.register("tiles", TileView, basename="tiles")

urlpatterns = [
    # path(
    #     "tiles/<str:geolevel>/<str:datatype>/<int:zoom>/<int:x>/<int:y>.mvt",
    #     views.tile_view,
    # ),
    # # path("feedback/", views.receive_feedback),
    path("", include(router.urls)),

]
