from django.contrib.gis.db.models import GeometryField, PolygonField
from django.contrib.gis.geos import GEOSGeometry
from django.db import models


class Tile(models.Model):
    """Square area of the map with the value of the indice."""

    geometry = PolygonField(srid=2154)
    indice = models.FloatField(null=True)


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
