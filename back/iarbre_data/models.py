from django.contrib.gis.db.models import GeometryField, PolygonField
from django.db import models
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.db.models import Avg

from api.constants import ModelType


class TileAggregateBase(models.Model):
    """Abstract base class for aggregating Tiles at IRIS and city level."""

    geometry = PolygonField(srid=2154)
    code = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def average_normalized_indice(self):
        """As for now the aggregate is the average but it may change later."""
        return self.tiles.aggregate(avg=Avg("plantability_normalized_indice"))["avg"]

    @property
    def average_indice(self):
        return self.tiles.aggregate(avg=Avg("plantability_indice"))["avg"]


class City(TileAggregateBase):
    """City model."""

    tiles_generated = models.BooleanField(default=False)
    tiles_computed = models.BooleanField(default=False)

    def __str__(self):
        return f"CITY name: {self.name}"


class Iris(TileAggregateBase):
    """IRIS is a statistical unit in France."""

    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="irises", null=True, blank=True
    )

    def __str__(self):
        return f"IRIS code: {self.code}"


class Tile(models.Model):
    """Elementary element on the map with the value of the indice."""

    geometry = PolygonField(srid=2154)
    map_geometry = PolygonField(srid=3857, null=True, blank=True)
    plantability_indice = models.FloatField(null=True)
    plantability_normalized_indice = models.FloatField(null=True, blank=True)

    type = ModelType.TILE.value

    iris = models.ForeignKey(
        Iris, on_delete=models.CASCADE, related_name="tiles", null=True, blank=True
    )
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="tiles", null=True, blank=True
    )

    @property
    def color(self):
        """Return the color of the tile based on the normalized indice."""
        if self.plantability_normalized_indice is None:
            return "purple"
        elif self.plantability_normalized_indice < 0.205:
            return "#E0E0E0"
        elif self.plantability_normalized_indice < 0.486:
            return "#F0F1C0"
        elif self.plantability_normalized_indice < 0.589:
            return "#E5E09A"
        elif self.plantability_normalized_indice < 0.682:
            return "#B7D990"
        elif self.plantability_normalized_indice < 0.826:
            return "#71BB72"
        else:
            return "#006837"

    def get_layer_properties(self):
        """Return the properties of the tile for the MVT layer."""
        return {
            "id": self.id,
            "indice": self.plantability_normalized_indice,
            "color": self.color,
        }


@receiver(pre_save, sender=Tile)
def before_save_tile(sender, instance, **kwargs):
    """Transform the geometry to the map geometry."""
    if instance.map_geometry is None:
        instance.map_geometry = instance.geometry.transform(3857, clone=True)


class Data(models.Model):
    """Land occupancy data"""

    geometry = GeometryField(srid=2154)
    metadata = models.CharField(max_length=50, null=True, blank=True)
    factor = models.CharField(max_length=50, null=True, blank=True)


class TileFactor(models.Model):
    """Factor of a tile.
    A factor value represent the proportion of land occupancy on the tile."""

    tile = models.ForeignKey(Tile, on_delete=models.CASCADE, related_name="factors")
    factor = models.CharField(max_length=50)
    value = models.FloatField()


class MVTTile(models.Model):
    """Model to store MVT tiles as danjo-media."""

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
    """Delete the file when the model is deleted."""
    instance.mvt_file.delete(save=False)


class Lcz(models.Model):
    """Elementary element on the map with the value of the LCZ description."""

    geometry = PolygonField(srid=2154)
    map_geometry = PolygonField(srid=3857, null=True, blank=True)
    lcz_indice = models.CharField(max_length=4, null=True)
    lcz_description = models.CharField(max_length=50, null=True)

    type = ModelType.LCZ.value

    @property
    def color(self):  # noqa: C901
        """Return the color of the tile based on the normalized indice."""
        if self.lcz_indice is None:
            return "purple"
        elif self.lcz_indice == "LCZ1":
            return "#8c0000"
        elif self.lcz_indice == "LCZ2":
            return "#d10000"
        elif self.lcz_indice == "LCZ3":
            return "#ff0000"
        elif self.lcz_indice == "LCZ4":
            return "#bf4d00"
        elif self.lcz_indice == "LCZ5":
            return "#fa6600"
        elif self.lcz_indice == "LCZ5":
            return "#ff9955"
        elif self.lcz_indice == "LCZ6":
            return "#faee05"
        elif self.lcz_indice == "LCZ7":
            return "#bcbcbc"
        elif self.lcz_indice == "LCZ8/10":
            return "#ffccaa"
        elif self.lcz_indice == "LCZ9":
            return "#006a00"
        elif self.lcz_indice == "LCZA":
            return "#00aa00"
        elif self.lcz_indice == "LCZB":
            return "#648525"
        elif self.lcz_indice == "LCZC":
            return ""
        elif self.lcz_indice == "LCZD":
            return "#b9db79"
        elif self.lcz_indice == "LCZE":
            return "#000000"
        elif self.lcz_indice == "LCZF":
            return "#fbf7ae"
        else:
            return "#6a6aff"

    def get_layer_properties(self):
        """Return the properties of the tile for the MVT layer."""
        return {
            "id": self.id,
            "indice": self.lcz_indice,
            "description": self.lcz_description,
            "color": self.color,
        }


@receiver(pre_save, sender=Lcz)
def before_save_lcz(sender, instance, **kwargs):
    """Transform the geometry to the map geometry."""
    if instance.map_geometry is None:
        instance.map_geometry = instance.geometry.transform(3857, clone=True)
