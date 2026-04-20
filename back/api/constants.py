from django.db.models import TextChoices

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


VEGESTRATE_FILES = {
    (2018, "02", False, None): "raw_fullmetropole_ir_02_2018.tif",
    (2018, "02", True, 3): "postprocessv3_fullmetropole_ir_02_2018.tif",
    (2023, "02", False, None): "raw_lyon_metropole_ir_02_2023.tif",
    (2023, "02", True, 1): "postprocessv1_fullmetropole_RGB_02_2023.tif",
    (2023, "02", True, 2): "postprocessv2_fullmetropole_ir_02_2023.tif",
    (2023, "02", True, 3): "postprocessv3_fullmetropole_ir_02_2023.tif",
}

VEGESTRATE_COLOR_MAP = {
    0: (0, 0, 0, 0),
    1: (200, 217, 111, 255),
    2: (58, 145, 68, 255),
    3: (20, 69, 47, 255),
}

_VEGESTRATE_LAYER_TITLES = {
    (2018, "02", False, None): (
        "iarbre:vegestrate_2018_raw",
        "Végéstrate 2018 - 20cm - brut",
    ),
    (2018, "02", True, 3): (
        "iarbre:vegestrate_2018_ppv3",
        "Végéstrate 2018 - 20cm - post-traitement v3",
    ),
    (2023, "02", False, None): (
        "iarbre:vegestrate_2023_raw",
        "Végéstrate 2023 - 20cm - brut",
    ),
    (2023, "02", True, 1): (
        "iarbre:vegestrate_2023_ppv1",
        "Végéstrate 2023 - 20cm - post-traitement v1",
    ),
    (2023, "02", True, 2): (
        "iarbre:vegestrate_2023_ppv2",
        "Végéstrate 2023 - 20cm - post-traitement v2",
    ),
    (2023, "02", True, 3): (
        "iarbre:vegestrate_2023_ppv3",
        "Végéstrate 2023 - 20cm - post-traitement v3",
    ),
}

WMS_LAYERS = {
    layer_name: {
        "title": title,
        "path": f"rasters/vegestrate/{VEGESTRATE_FILES[key]}",
        "color_map": VEGESTRATE_COLOR_MAP,
    }
    for key, (layer_name, title) in _VEGESTRATE_LAYER_TITLES.items()
}

# Score ranges for different data types
PLANTABILITY_MAX_SCORE = 10
VULNERABILITY_MAX_SCORE = 9

# Rounding precision for calculated indices
INDICE_ROUNDING_DECIMALS = 1
