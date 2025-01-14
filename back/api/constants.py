from django.db.models import TextChoices


class ModelType(TextChoices):
    TILE = "tile", "Tile"
    CITY = "city", "City"
    IRIS = "iris", "Iris"
