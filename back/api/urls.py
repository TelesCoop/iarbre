from django.urls import path

from api import views

urlpatterns = [
    path(
        "tiles/<str:model_type>/<str:layer>/<int:zoom>/<int:x>/<int:y>.mvt",
        views.tile_view,
    ),
]
