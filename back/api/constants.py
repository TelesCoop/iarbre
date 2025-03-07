from django.db.models import TextChoices


class GeoLevel(TextChoices):
    TILE = "tile", "Tile"
    CITY = "city", "City"
    IRIS = "iris", "Iris"
    LCZ = "lcz", "LCZ"


class DataType(TextChoices):
    LCZ = "lcz", "LCZ"
    TILE = "plantability", "Plantability"
