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
    (2015, "08", True, 3, "elevation"): "../WMS/vegestrate_08_2015_elevation.tif",
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

HEAT_FILES = {
    "pet_index": "PET_index.tif",
    "sun_exposure": "SunExposure.tif",
}

HOURLY_HEAT_LAYERS = {"pet_index"}

PET_INDEX_COLOR_MAP = {
    5: (255, 255, 204, 255),
    6: (254, 217, 118, 255),
    7: (253, 141, 60, 255),
    8: (227, 26, 28, 255),
    9: (128, 0, 38, 255),
}

SUN_EXPOSURE_COLOR_BINS = [
    (0.0, (255, 255, 204, 255)),
    (0.2, (255, 237, 160, 255)),
    (0.4, (254, 217, 118, 255)),
    (0.6, (254, 178, 76, 255)),
    (0.8, (253, 141, 60, 255)),
    (0.9, (240, 59, 32, 255)),
]

VEGESTRATE_COLOR_MAP = {
    0: (0, 0, 0, 0),
    1: (200, 217, 111, 255),
    2: (58, 145, 68, 255),
    3: (20, 69, 47, 255),
}


def _build_elevation_color_map():
    _bins = [
        (0, 1, (237, 245, 233, 255)),
        (1, 2, (199, 219, 192, 255)),
        (2, 4, (151, 176, 144, 255)),
        (4, 7, (122, 147, 116, 255)),
        (7, 10, (109, 135, 102, 255)),
        (10, 15, (66, 106, 69, 255)),
        (15, 20, (73, 103, 63, 255)),
        (20, 26, (52, 82, 42, 255)),
        (26, 33, (43, 72, 34, 255)),
        (33, 41, (0, 40, 20, 255)),
    ]
    result = {}
    for start, end, color in _bins:
        for v in range(start, end):
            result[v] = color
    return result


VEGESTRATE_ELEVATION_COLOR_MAP = _build_elevation_color_map()

# Score ranges for different data types
PLANTABILITY_MAX_SCORE = 10
VULNERABILITY_MAX_SCORE = 9

# Rounding precision for calculated indices
INDICE_ROUNDING_DECIMALS = 1
