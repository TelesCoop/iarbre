from django.contrib.gis.db.models import GeometryField, PolygonField
from django.db import models
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.db.models import Avg

from api.constants import ModelType


class TileAggregateBase(models.Model):
    """Abstract base class for aggregating Tiles."""

    geometry = PolygonField(srid=2154)
    code = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def average_normalized_indice(self):
        """As for now the aggregate is the average but it may change later."""
        return self.tiles.aggregate(avg=Avg("normalized_indice"))["avg"]

    @property
    def average_indice(self):
        return self.tiles.aggregate(avg=Avg("indice"))["avg"]


class City(TileAggregateBase):
    def __str__(self):
        return f"CITY name: {self.name}"


class Iris(TileAggregateBase):
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="irises", null=True, blank=True
    )

    def __str__(self):
        return f"IRIS code: {self.code}"


class Tile(models.Model):
    """Elementary element on the map with the value of the indice."""

    geometry = PolygonField(srid=2154)
    map_geometry = PolygonField(srid=3857, null=True, blank=True)
    indice = models.FloatField(null=True)
    normalized_indice = models.FloatField(null=True, blank=True)

    type = ModelType.TILE.value

    iris = models.ForeignKey(
        Iris, on_delete=models.CASCADE, related_name="tiles", null=True, blank=True
    )
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="tiles", null=True, blank=True
    )

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


class TileFactor(models.Model):
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE, related_name="factors")
    factor = models.CharField(max_length=50)
    value = models.FloatField()


class MVTTile(models.Model):
    zoom_level = models.IntegerField()
    tile_x = models.IntegerField()
    tile_y = models.IntegerField()
    model_type = models.CharField(max_length=50)
    mvt_file = models.FileField(upload_to="mvt_files/")

    def save_mvt(self, mvt_data, filename):
        """Save the MVT data into the FileField."""
        content = ContentFile(mvt_data)
        self.mvt_file.save(filename, content, save=False)
        self.save()

    def __str__(self):
        return f"Tile {self.model_type}/{self.zoom_level}/{self.tile_x}/{self.tile_y}"


@receiver(pre_delete, sender=MVTTile)
def before_delete_mvt_tile(sender, instance, **kwargs):
    instance.mvt_file.delete(save=False)
