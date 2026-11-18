from iarbre_data.data_config import FINE_GRID_FACTORS
from iarbre_data.models import Data, Vegestrate
from iarbre_data.utils.factor_margin import is_fine_grid

Layer = tuple[str, str]

LAYER_QUERYSETS = {
    "data": lambda factor: Data.objects.filter(factor=factor),
    "vegestrate": lambda strate: Vegestrate.objects.filter(strate=strate),
}


def get_layer_queryset(layer: Layer):
    kind, value = layer
    return LAYER_QUERYSETS[kind](value)


def get_factor_layers(factor_name: str, grid_size: int) -> tuple[list, list]:
    if is_fine_grid(grid_size) and factor_name in FINE_GRID_FACTORS:
        layers = FINE_GRID_FACTORS[factor_name]
        return layers["include"], layers.get("exclude", [])
    return [("data", factor_name)], []
