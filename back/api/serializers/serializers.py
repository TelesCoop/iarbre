import json

from rest_framework import serializers

from api.constants import DataType, GeoLevel
from iarbre_data.models import City, Iris, Lcz, Tile, Vegestrate, Vulnerability


class LczSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lcz
        fields = (
            "id",
            "geometry",
            "map_geometry",
            "lcz_index",
            "lcz_description",
            "details",
            "geolevel",
            "datatype",
        )


class TileSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()

    class Meta:
        model = Tile

        fields = (
            "id",
            "plantability_normalized_indice",
            "plantability_indice",
            "details",
            "geolevel",
            "datatype",
        )

    def get_details(self, obj):
        if isinstance(obj.details, str):
            try:
                return json.loads(obj.details)
            except json.JSONDecodeError:
                return None
        return obj.details


class VulnerabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vulnerability
        fields = (
            "id",
            "geometry",
            "map_geometry",
            "vulnerability_index_day",
            "vulnerability_index_night",
            "expo_index_day",
            "expo_index_night",
            "capaf_index_day",
            "capaf_index_night",
            "sensibilty_index_day",
            "sensibilty_index_night",
            "details",
            "geolevel",
            "datatype",
        )


class CitySerializer(serializers.ModelSerializer):
    plantabilityCounts = serializers.JSONField(source="plantability_counts")
    averageNormalizedIndice = serializers.FloatField(source="average_normalized_indice")
    averageIndice = serializers.FloatField(source="average_indice")
    treesSurface = serializers.FloatField(source="trees_surface")
    bushesSurface = serializers.FloatField(source="bushes_surface")
    grassSurface = serializers.FloatField(source="grass_surface")
    totalVegetationSurface = serializers.FloatField(source="total_vegetation_surface")

    class Meta:
        model = City
        fields = (
            "id",
            "code",
            "name",
            "plantabilityCounts",
            "averageNormalizedIndice",
            "averageIndice",
            "treesSurface",
            "bushesSurface",
            "grassSurface",
            "totalVegetationSurface",
        )


class IrisSerializer(serializers.ModelSerializer):
    plantabilityCounts = serializers.JSONField(source="plantability_counts")
    averageNormalizedIndice = serializers.FloatField(source="average_normalized_indice")
    averageIndice = serializers.FloatField(source="average_indice")

    class Meta:
        model = Iris
        fields = (
            "id",
            "code",
            "name",
            "city",
            "plantabilityCounts",
            "averageNormalizedIndice",
            "averageIndice",
        )


class VegestrateSerializer(serializers.ModelSerializer):
    indice = serializers.CharField(source="strate")

    class Meta:
        model = Vegestrate
        fields = ("id", "indice", "surface", "geolevel", "datatype")


class SoilOccupancySerializer(serializers.Serializer):
    """Serializer for a soil occupancy sample at a given point.

    Used as explicability data for the biodiv (vegestrate) layer.
    """

    class_id = serializers.IntegerField()
    code = serializers.CharField()
    label = serializers.CharField(allow_null=True)
    datatype = serializers.SerializerMethodField()
    geolevel = serializers.SerializerMethodField()

    def get_datatype(self, _obj):
        return DataType.SOIL_OCCUPANCY.value

    def get_geolevel(self, _obj):
        return GeoLevel.TILE.value


class BaseScoresSerializer(serializers.Serializer):
    """Base serializer for scores within a polygon"""

    datatype = serializers.CharField()
    count = serializers.IntegerField()
    iris_codes = serializers.ListField(child=serializers.CharField())
    city_codes = serializers.ListField(child=serializers.CharField())


class PlantabilityScoresSerializer(BaseScoresSerializer):
    plantability_normalized_indice = serializers.FloatField()
    plantability_indice = serializers.FloatField()
    distribution = serializers.DictField()


class VulnerabilityScoresSerializer(BaseScoresSerializer):
    vulnerability_indice_day = serializers.FloatField()
    vulnerability_indice_night = serializers.FloatField()


class PlantabilityVulnerabilityScoresSerializer(
    PlantabilityScoresSerializer, VulnerabilityScoresSerializer
):
    pass
