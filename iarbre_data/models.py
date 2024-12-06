from django.contrib.gis.db.models import GeometryField, PolygonField
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from api.constants import ModelType
from iarbre_data.management.commands.utils import (
    transform_geometry_to_srid_and_simplify,
)


class Tile(models.Model):
    """Square area of the map with the value of the indice."""

    geometry = PolygonField(srid=2154)
    map_geometry = PolygonField(srid=3857, null=True)
    indice = models.FloatField(null=True)

    type = ModelType.TILE.value

    @property
    def color(self):
        if self.indice is None:
            return "purple"
        elif self.indice < -1.25:
            return "#676767"
        elif self.indice < -0.75:
            return "#A63F28"
        elif self.indice < -0.15:
            return "#D98B2B"
        elif self.indice < 0.15:
            return "#F3EFE9"
        elif self.indice < 0.85:
            return "#BEE2A4"
        else:
            return "#5AA055"

    def get_layer_properties(self):
        return {
            "id": self.id,
            "indice": self.indice,
            "color": self.color,
        }


@receiver(pre_save, sender=Tile)
def before_save_tile(sender, instance, **kwargs):
    if instance.map_geometry is None:
        instance.map_geometry = transform_geometry_to_srid_and_simplify(
            instance.geometry
        )


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
