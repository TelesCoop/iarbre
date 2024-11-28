from django.contrib.gis.db.models import GeometryField, PolygonField
from django.db import models

from api.constants import ModelType


class Tile(models.Model):
    """Square area of the map with the value of the indice."""

    geometry = PolygonField(srid=2154)
    indice = models.FloatField(null=True)

    type = ModelType.TILE.value

    @property
    def color(self):
        if self.indice is None:
            return "white"
        elif self.indice < 0.3:
            return "green"
        elif self.indice < 0.6:
            return "yellow"
        else:
            return "red"

    def get_layer_properties(self):
        return {
            "id": self.id,
            "indice": self.indice,
            "color": self.color,
        }


@models.signals.pre_save.connect
def before_save_tile(sender, instance, **kwargs):
    # check if instance has attribute geometry for migration
    if hasattr(instance, "geometry"):
        instance.geom = instance.geometry.transform(4326, clone=True)


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
