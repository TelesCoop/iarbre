from django.urls import path

from api import views

urlpatterns = [
    path(
        "tiles/<str:geolevel>/<str:datatype>/<int:zoom>/<int:x>/<int:y>.mvt",
        views.tile_view,
    ),
    path("feedback/", views.receive_feedback),
]
