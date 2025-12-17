import json

from rest_framework import serializers

from iarbre_data.models import City, Iris, Lcz, Tile, Vulnerability


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

    class Meta:
        model = City
        fields = (
            "id",
            "code",
            "name",
            "plantabilityCounts",
            "averageNormalizedIndice",
            "averageIndice",
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
