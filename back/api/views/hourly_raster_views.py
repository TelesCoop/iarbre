from pathlib import Path

from django.conf import settings
from rest_framework.exceptions import ValidationError

from api.constants import PET_RASTERS, SHADOW_RASTER
from api.views.raster_tile_views import RasterTileView
from iarbre_data.utils.hourly_rasters import hour_raster_path

HOURS = range(25)


def _int_param(request, name: str, allowed) -> int:
    try:
        value = int(request.query_params.get(name, ""))
    except ValueError:
        value = None
    if value not in allowed:
        raise ValidationError({name: f"Must be one of {', '.join(map(str, allowed))}."})
    return value


class HourlyRasterTileView(RasterTileView):
    def raster_name(self, request) -> str:
        raise NotImplementedError

    def raster_path(self, request) -> Path:
        hour = _int_param(request, "hour", HOURS)
        source = (
            Path(settings.MEDIA_ROOT)
            / "rasters/WMS"
            / f"{self.raster_name(request)}.tif"
        )
        return hour_raster_path(source, hour)

    def render(self, data, nodata, request):
        return self.encode_terrarium(data, nodata)


class PetTileView(HourlyRasterTileView):
    def raster_name(self, request) -> str:
        return PET_RASTERS[_int_param(request, "year", list(PET_RASTERS))]


class ShadowTileView(HourlyRasterTileView):
    def raster_name(self, request) -> str:
        return SHADOW_RASTER
