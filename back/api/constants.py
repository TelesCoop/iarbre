from django.db.models import TextChoices


class ModelType(TextChoices):
    TILE = "tile", "Tile"
