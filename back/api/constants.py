from django.db.models import TextChoices

DEFAULT_ZOOM_LEVELS = (10, 18)

ZOOM_TO_GRID_SIZE = {10: 75, 11: 50, 12: 50, 13: 20, 14: 10, 15: 10}


class GeoLevel(TextChoices):
    TILE = "tile", "Tile"
    CITY = "city", "City"
    IRIS = "iris", "Iris"
    LCZ = "lcz", "LCZ"
    CADASTRE = "cadastre", "Cadastre"


class DataType(TextChoices):
    LCZ = "lcz", "LCZ"
    TILE = "plantability", "Plantability"
    VULNERABILITY = "vulnerability", "Vulnerability"
    CADASTRE = "cadastre", "Cadastre"
    VEGESTRATE = "vegestrate", "Vegestrate"
    SOIL_OCCUPANCY = "soil_occupancy", "Soil occupancy"


# Path (relative to MEDIA_ROOT) of the COSIA-derived land cover raster that
# provides the biodiv layer's soil occupancy explicability data.
SOIL_OCCUPANCY_RASTER_PATH = "rasters/OccupationSol.tif"

# COSIA (IGN) land cover nomenclature — 15 classes.
# Class ids follow the IGN public COSIA ordering. If the specific raster
# uses a different encoding, update this mapping accordingly.
# Source: https://geoservices.ign.fr/cosia
SOIL_OCCUPANCY_CLASSES = {
    1: {"code": "building", "label": "Bâtiment"},
    2: {"code": "pervious", "label": "Zone perméable"},
    3: {"code": "impervious", "label": "Zone imperméable"},
    4: {"code": "swimming_pool", "label": "Piscine"},
    5: {"code": "greenhouse", "label": "Serre"},
    6: {"code": "bare_soil", "label": "Sol nu"},
    7: {"code": "water", "label": "Surface d'eau"},
    8: {"code": "snow", "label": "Neige"},
    9: {"code": "coniferous", "label": "Conifère"},
    10: {"code": "deciduous", "label": "Feuillu"},
    11: {"code": "brushwood", "label": "Broussaille"},
    12: {"code": "vineyard", "label": "Vigne"},
    13: {"code": "crops", "label": "Culture"},
    14: {"code": "plowed_land", "label": "Terre labourée"},
    15: {"code": "grassland", "label": "Pelouse"},
}


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
