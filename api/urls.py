from django.urls import path

from api import views
from api.views import serve_mbtiles
from iarbre_data import settings

urlpatterns = [
    # path("tiles/<str:model_type>/<int:zoom>/<int:x>/<int:y>", views.tile_view),
    path('<str:tileset>/<int:z>/<int:x>/<int:y>.mvt', serve_mbtiles, name='mbtiles_serve'),
    # path('<str:tileset>/<int:z>/<int:x>/<int:y>.pbf', serve_mbtiles, name='mbtiles_serve'),

]

