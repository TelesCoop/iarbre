from pathlib import Path

import numpy as np
import rasterio
from django.conf import settings
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from pyproj import Transformer
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from api.views.hourly_raster_views import _int_param
from api.views.raster_tile_views import RasterTileView
from iarbre_data.data_config import FACTORS
from iarbre_data.management.commands.raster_to_land_use import compute_top5_land_use
from plantability.constants import (
    BLOCKED_SCORE,
    PLANTABILITY_NORMALIZED,
    PLANTABILITY_THRESHOLDS,
)

GRIDS = (5, 1)


def grid_param(request) -> int:
    return _int_param(request, "grid", GRIDS)


def score_raster_path(grid: int) -> Path:
    return (
        Path(settings.MEDIA_ROOT)
        / "rasters/plantability_2026"
        / f"plantability_2026_villeurbanne_{grid}m.tif"
    )


def score_classes(scores: np.ndarray) -> np.ndarray:
    return np.asarray(PLANTABILITY_NORMALIZED, dtype=np.float32)[
        np.digitize(scores, PLANTABILITY_THRESHOLDS[:-1], right=True)
    ]


class Plantability2026TileView(RasterTileView):
    @method_decorator(never_cache)
    def get(self, request, z, x, y):
        return self.tile_response(request, z, x, y)

    def raster_path(self, request) -> Path:
        return score_raster_path(grid_param(request))

    def render(self, data, nodata, request):
        classes = score_classes(data)
        classes[(data == nodata) | (data == BLOCKED_SCORE)] = nodata
        return self.encode_terrarium(classes, nodata)


def _float_param(request, name: str) -> float:
    try:
        return float(request.query_params[name])
    except (KeyError, ValueError):
        raise ValidationError({name: "Must be a number."})


class Plantability2026PointView(APIView):
    @method_decorator(never_cache)
    def get(self, request):
        lat = _float_param(request, "lat")
        lng = _float_param(request, "lng")
        grid = grid_param(request)
        score_path = score_raster_path(grid)
        if not score_path.exists():
            raise Http404("Raster file not found")

        with rasterio.open(score_path) as src:
            x, y = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True).transform(
                lng, lat
            )
            b = src.bounds
            if not (b.left <= x < b.right and b.bottom < y <= b.top):
                raise Http404("Point outside raster")
            row, col = src.index(x, y)
            (score,) = next(src.sample([(x, y)]))
            if score == src.nodata:
                raise Http404("No data at this point")

        factors_folder = score_path.parent / f"factors_{grid}m"
        land_uses = {}
        for factor_path in factors_folder.glob("*.tif"):
            if factor_path.stem not in FACTORS:
                continue
            with rasterio.open(factor_path) as src:
                (value,) = next(src.sample([(x, y)]))
            if value > 0:
                land_uses[factor_path.stem] = float(value)

        return Response(
            {
                "id": f"{grid}m-{row}-{col}",
                "plantability_indice": float(score),
                "plantability_normalized_indice": float(
                    score_classes(np.array([score]))[0]
                ),
                "details": {"top5_land_use": compute_top5_land_use(land_uses)},
            }
        )
