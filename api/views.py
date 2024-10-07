from django.shortcuts import render
from django.views.decorators.http import require_GET

from api.map import territories_to_tile


# Create your views here.


@require_GET
def tile_view(request, zoom, x, y):
    params = {}
    model = None
    return territories_to_tile(model, x, y, zoom, params)