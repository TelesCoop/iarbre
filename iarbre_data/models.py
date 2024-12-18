from django.contrib.gis.db.models import GeometryField, PolygonField
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from api.constants import ModelType


class Tile(models.Model):
    """Square area of the map with the value of the indice."""

    geometry = PolygonField(srid=2154)
    map_geometry = PolygonField(srid=3857, null=True, blank=True)
    indice = models.FloatField(null=True)
    normalized_indice = models.FloatField(null=True, blank=True)

    type = ModelType.TILE.value

    @property
    def color(self):
        if self.normalized_indice is None:
            return "purple"
        elif self.normalized_indice < 0.455:
            return "#676767"
        elif self.normalized_indice < 0.482:
            return "#A63F28"
        elif self.normalized_indice < 0.511:
            return "#D98B2B"
        elif self.normalized_indice < 0.546:
            return "#F3EFE9"
        elif self.normalized_indice < 0.67:
            return "#BEE2A4"
        else:
            return "#5AA055"

    def get_layer_properties(self):
        return {
            "id": self.id,
            "indice": self.normalized_indice,
            "color": self.color,
        }


@receiver(pre_save, sender=Tile)
def before_save_tile(sender, instance, **kwargs):
    if instance.map_geometry is None:
        instance.map_geometry = instance.geometry.transform(3857, clone=True)


class Data(models.Model):
    geometry = GeometryField(srid=2154)
    metadata = models.CharField(max_length=50, null=True, blank=True)
    factor = models.CharField(max_length=50, null=True, blank=True)


class City(models.Model):
    geometry = PolygonField(srid=2154)
    name = models.CharField(max_length=50)
    insee_code = models.CharField(max_length=10)


class TileFactor(models.Model):
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE)
    factor = models.CharField(max_length=50)
    value = models.FloatField()
