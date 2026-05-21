from django.db.models import TextChoices

from iarbre_data.utils.calque_config import CALQUE_REGISTRY, render_fn_from_color_map
from iarbre_data.utils.palettes import (
    VEGESTRATE_COLOR_MAP,
    VEGESTRATE_ELEVATION_COLOR_MAP,
)

DEFAULT_ZOOM_LEVELS = (10, 18)

ZOOM_TO_GRID_SIZE = {10: 75, 11: 50, 12: 50, 13: 20, 14: 10, 15: 10}


class GeoLevel(TextChoices):
    TILE = "tile", "Tile"
    CITY = "city", "City"
    IRIS = "iris", "Iris"
    LCZ = "lcz", "LCZ"
    CADASTRE = "cadastre", "Cadastre"
    BIOSPHERE_FUNCTIONAL_INTEGRITY = (
        "biosphere_functional_integrity",
        "Biosphere Functional Integrity",
    )


class DataType(TextChoices):
    LCZ = "lcz", "LCZ"
    TILE = "plantability", "Plantability"
    VULNERABILITY = "vulnerability", "Vulnerability"
    CADASTRE = "cadastre", "Cadastre"
    BIOSPHERE_FUNCTIONAL_INTEGRITY = (
        "biosphere_functional_integrity",
        "Biosphere Functional Integrity",
    )
    LIDAR = "vegetation", "Vegetation"
    VEGESTRATE = "vegestrate", "Vegestrate"


class FrontendDataType(TextChoices):
    """DataType enum used by the frontend"""

    PLANTABILITY = "plantability", "Plantability"
    VULNERABILITY = "vulnerability", "Vulnerability"
    CLIMATE_ZONE = "lcz", "LCZ"
    PLANTABILITY_VULNERABILITY = (
        "plantability_vulnerability",
        "Plantability & Vulnerability",
    )
    VEGESTRATE = ("vegestrate", "Vegestrate")


# Score ranges for different data types
PLANTABILITY_MAX_SCORE = 10
VULNERABILITY_MAX_SCORE = 9

# Rounding precision for calculated indices
INDICE_ROUNDING_DECIMALS = 1

VEGESTRATE_FILES = {
    (2018, "02", False, None, "class"): "raw_fullmetropole_ir_02_2018.tif",
    (2018, "02", True, 3, "class"): "postprocessv3_fullmetropole_ir_02_2018.tif",
    (2023, "02", False, None, "class"): "raw_lyon_metropole_ir_02_2023.tif",
    (2023, "02", True, 1, "class"): "postprocessv1_fullmetropole_RGB_02_2023.tif",
    (2023, "02", True, 2, "class"): "postprocessv2_fullmetropole_ir_02_2023.tif",
    (2023, "02", True, 3, "class"): "postprocessv3_fullmetropole_ir_02_2023.tif",
    (
        2023,
        "02",
        True,
        3,
        "elevation",
    ): "postprocessv3_fullmetropole_ir_02_2023_elevation_median.tif",
}

_VEGESTRATE_LAYER_TITLES = {
    (2018, "02", False, None, "class"): (
        "iarbre:vegestrate_2018_raw",
        "Végéstrate 2018 - 20cm - brut",
    ),
    (2018, "02", True, 3, "class"): (
        "iarbre:vegestrate_2018_ppv3",
        "Végéstrate 2018 - 20cm - post-traitement v3",
    ),
    (2023, "02", False, None, "class"): (
        "iarbre:vegestrate_2023_raw",
        "Végéstrate 2023 - 20cm - brut",
    ),
    (2023, "02", True, 1, "class"): (
        "iarbre:vegestrate_2023_ppv1",
        "Végéstrate 2023 - 20cm - post-traitement v1",
    ),
    (2023, "02", True, 2, "class"): (
        "iarbre:vegestrate_2023_ppv2",
        "Végéstrate 2023 - 20cm - post-traitement v2",
    ),
    (2023, "02", True, 3, "class"): (
        "iarbre:vegestrate_2023_ppv3",
        "Végéstrate 2023 - 20cm - post-traitement v3",
    ),
    (2023, "02", True, 3, "elevation"): (
        "iarbre:vegestrate_2023_ppv3_elevation",
        "Végéstrate 2023 - 20cm - post-traitement v3 - hauteur (nDSM avec filtrage médian)",
    ),
}

WMS_LAYERS = {
    layer_name: {
        "title": title,
        "path": f"rasters/vegestrate/{VEGESTRATE_FILES[key]}",
        "render_fn": render_fn_from_color_map(
            VEGESTRATE_ELEVATION_COLOR_MAP
            if key[4] == "elevation"
            else VEGESTRATE_COLOR_MAP
        ),
    }
    for key, (layer_name, title) in _VEGESTRATE_LAYER_TITLES.items()
}

WMS_LAYERS.update(
    {
        f"iarbre:{name}": {
            "title": cfg.title,
            "path": f"rasters/{cfg.tif_path or name + '.tif'}",
            "render_fn": cfg.make_render_fn(),
        }
        for name, cfg in CALQUE_REGISTRY.items()
    }
)
