from pathlib import Path

from django.conf import settings
from django.http import Http404
from rest_framework.exceptions import ValidationError

from api.constants import PET_RASTERS
from api.views.raster_tile_views import RasterTileView
from iarbre_data.utils.hourly_rasters import hour_raster_path, is_up_to_date
from iarbre_data.utils.palettes import PET_COLOR_MAP

PET_HOURS = range(25)


def _int_param(request, name: str, allowed) -> int:
    try:
        value = int(request.query_params.get(name, ""))
    except ValueError:
        value = None
    if value not in allowed:
        raise ValidationError({name: f"Must be one of {', '.join(map(str, allowed))}."})
    return value


class PetTileView(RasterTileView):
    def raster_path(self, request) -> Path:
        year = _int_param(request, "year", list(PET_RASTERS))
        hour = _int_param(request, "hour", PET_HOURS)
        source = Path(settings.MEDIA_ROOT) / "rasters/WMS" / f"{PET_RASTERS[year]}.tif"
        hour_path = hour_raster_path(source, hour)
        if not (source.exists() and is_up_to_date(source, hour_path)):
            raise Http404(f"File not found: {hour_path.name}.")
        return hour_path

    def render(self, data, nodata, request):
        return self.colorize(data, PET_COLOR_MAP)
