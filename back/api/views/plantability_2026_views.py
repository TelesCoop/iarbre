from pathlib import Path

import numpy as np
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from api.views.hourly_raster_views import _int_param
from api.views.raster_tile_views import RasterTileView
from plantability.constants import (
    BLOCKED_SCORE,
    PLANTABILITY_NORMALIZED,
    PLANTABILITY_THRESHOLDS,
)

GRIDS = (5, 1)


class Plantability2026TileView(RasterTileView):
    @method_decorator(never_cache)
    def get(self, request, z, x, y):
        return self.tile_response(request, z, x, y)

    def raster_path(self, request) -> Path:
        grid = _int_param(request, "grid", GRIDS)
        return (
            Path(settings.MEDIA_ROOT)
            / "rasters/plantability_2026"
            / f"plantability_2026_villeurbanne_{grid}m.tif"
        )

    def render(self, data, nodata, request):
        classes = np.asarray(PLANTABILITY_NORMALIZED, dtype=np.float32)[
            np.digitize(data, PLANTABILITY_THRESHOLDS[:-1], right=True)
        ]
        classes[(data == nodata) | (data == BLOCKED_SCORE)] = nodata
        return self.encode_terrarium(classes, nodata)
