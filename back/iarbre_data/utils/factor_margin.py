from iarbre_data.data_config import (
    BLOCKING_SCORE,
    DATA_FILES,
    FACTORS,
    FINE_GRID_FACTORS,
    URL_FILES,
)

LEGACY_GRID_SIZE = 5


def get_factor_uncertainty(factor_name: str) -> float | None:
    for source in DATA_FILES + URL_FILES:
        if factor_name in source["factors"]:
            return source["uncertainty"]
    raise KeyError(f"No data source declares the factor {factor_name}")


def is_fine_grid(grid_size: int) -> bool:
    return grid_size < LEGACY_GRID_SIZE


def get_factor_margin(factor_name: str, grid_size: int) -> float:
    if not is_fine_grid(grid_size) or FACTORS[factor_name] != BLOCKING_SCORE:
        return 0.0
    uncertainty = get_factor_uncertainty(factor_name)
    if uncertainty is None:
        raise ValueError(f"Blocking factor {factor_name} needs an uncertainty")
    return float(uncertainty)


def get_factor_blur(factor_name: str, grid_size: int) -> float:
    if not is_fine_grid(grid_size) or FACTORS[factor_name] == BLOCKING_SCORE:
        return 0.0
    layers = FINE_GRID_FACTORS.get(factor_name, {})
    uncertainty = layers.get("uncertainty", get_factor_uncertainty(factor_name))
    return float(uncertainty or 0)
