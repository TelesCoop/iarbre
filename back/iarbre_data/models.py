from django.contrib.gis.db.models import GeometryField, PolygonField
from django.db import models
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.db.models import Avg

from iarbre_data.settings import TARGET_MAP_PROJ
from api.constants import GeoLevel, DataType


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
    map_geometry = PolygonField(srid=TARGET_MAP_PROJ, null=True, blank=True)
    plantability_indice = models.FloatField(null=True)
    plantability_normalized_indice = models.FloatField(null=True, blank=True)

    geolevel = GeoLevel.TILE.value
    datatype = DataType.TILE.value

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
        """Return the properties of the tile for the MVT datatype."""
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
    geolevel = models.CharField(max_length=50, choices=GeoLevel.choices)
    datatype = models.CharField(
        max_length=50, choices=DataType.choices, default=DataType.TILE.value
    )
    mvt_file = models.FileField(upload_to="mvt_files/")

    def save_mvt(self, mvt_data, filename):
        """Save the MVT data into the FileField."""
        content = ContentFile(mvt_data)
        print("fiename is ", filename)
        self.mvt_file.save(filename, content, save=False)
        self.save()

    def __str__(self):
        return f"Tile {self.mvt_file.path}"


@receiver(pre_delete, sender=MVTTile)
def before_delete_mvt_tile(sender, instance, **kwargs):
    """Delete the file when the model is deleted."""
    instance.mvt_file.delete(save=False)


class Lcz(models.Model):
    """Elementary element on the map with the value of the LCZ description."""

    geometry = PolygonField(srid=2154)
    map_geometry = PolygonField(srid=TARGET_MAP_PROJ, null=True, blank=True)
    lcz_index = models.CharField(max_length=4, null=True)
    lcz_description = models.CharField(max_length=50, null=True)

    geolevel = GeoLevel.LCZ.value
    datatype = DataType.LCZ.value

    @property
    def color(self):
        """Color defined by CEREMA in
        https://www.data.gouv.fr/fr/datasets/r/f80e08a4-ecd1-42a2-a8d6-963af16aec75"""
        color_map = {
            None: "purple",
            "1": "#8C0000",
            "2": "#D10000",
            "3": "#FF0000",
            "4": "#BF4D00",
            "5": "#fa6600",
            "6": "#ff9955",
            "7": "#faee05",
            "8": "#bcbcbc",
            "9": "#ffccaa",
            "A": "#006a00",
            "B": "#00aa00",
            "C": "#648525",
            "D": "#b9db79",
            "E": "#fbf7ae",
            "F": "#FBF7AE",
        }
        return color_map.get(self.lcz_index, "#6A6AFF")

    def get_layer_properties(self):
        """Return the properties of the tile for the MVT datatype."""
        return {
            "id": self.id,
            "indice": self.lcz_index,
            "description": self.lcz_description,
            "color": self.color,
        }


@receiver(pre_save, sender=Lcz)
def before_save_lcz(sender, instance, **kwargs):
    """Transform the geometry to the map geometry."""
    if instance.map_geometry is None:
        instance.map_geometry = instance.geometry.transform(3857, clone=True)


class Feedback(models.Model):
    """Store feedbacks from carte.iarbre.fr"""

    email = models.EmailField(blank=True, null=True)
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.email or 'Anonymous'}"
