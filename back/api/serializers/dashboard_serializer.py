from rest_framework import serializers


class DashboardCitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()


class DashboardPlantabilityDivisionSerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()
    averageNormalizedIndice = serializers.FloatField()
    distribution = serializers.DictField()


class DashboardPlantabilitySerializer(serializers.Serializer):
    averageNormalizedIndice = serializers.FloatField()
    distribution = serializers.DictField()
    distributionByDivision = DashboardPlantabilityDivisionSerializer(many=True)


class DashboardVulnerabilitySerializer(serializers.Serializer):
    averageDay = serializers.FloatField()
    averageNight = serializers.FloatField()
    expoDay = serializers.FloatField()
    expoNight = serializers.FloatField()
    sensibilityDay = serializers.FloatField()
    sensibilityNight = serializers.FloatField()
    capafDay = serializers.FloatField()
    capafNight = serializers.FloatField()


class DashboardVegetationSerializer(serializers.Serializer):
    totalHa = serializers.FloatField()
    treesSurfaceHa = serializers.FloatField()
    bushesSurfaceHa = serializers.FloatField()
    grassSurfaceHa = serializers.FloatField()


class DashboardLczSerializer(serializers.Serializer):
    averageBuildingSurfaceRate = serializers.FloatField()
    averageBuildingHeight = serializers.FloatField()
    impermeableSurfaceRate = serializers.FloatField()
    permeableSoilRate = serializers.FloatField()
    buildingRate = serializers.FloatField()
    treeCoverRate = serializers.FloatField()
    totalVegetationRate = serializers.FloatField()
    waterRate = serializers.FloatField()


class DashboardSerializer(serializers.Serializer):
    city = DashboardCitySerializer(allow_null=True)
    areaHa = serializers.FloatField()
    plantability = DashboardPlantabilitySerializer()
    vulnerability = DashboardVulnerabilitySerializer()
    vegetation = DashboardVegetationSerializer()
    lcz = DashboardLczSerializer()
