from django.db.models import TextChoices

DEFAULT_ZOOM_LEVELS = (10, 18)

ZOOM_TO_GRID_SIZE = {10: 100, 11: 75, 12: 75, 13: 30, 14: 15, 15: 10}


class GeoLevel(TextChoices):
    TILE = "tile", "Tile"
    CITY = "city", "City"
    IRIS = "iris", "Iris"
    LCZ = "lcz", "LCZ"


class DataType(TextChoices):
    LCZ = "lcz", "LCZ"
    TILE = "plantability", "Plantability"
    VULNERABILITY = "vulnerability", "Vulnerability"
