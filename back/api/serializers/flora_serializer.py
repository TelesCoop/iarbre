from rest_framework import serializers


class LocalFloraSummarySerializer(serializers.Serializer):
    totalSpeciesObserved = serializers.IntegerField(source="total_species_observed")
    dominantFamilies = serializers.ListField(
        child=serializers.CharField(), source="dominant_families"
    )
    dominantGenera = serializers.ListField(
        child=serializers.CharField(), source="dominant_genera"
    )


class TreeRecommendationSerializer(serializers.Serializer):
    scientificName = serializers.CharField(source="scientific_name")
    commonName = serializers.CharField(source="common_name")
    score = serializers.IntegerField()
    isNative = serializers.BooleanField(source="is_native")
    description = serializers.CharField()
    matchedCompanions = serializers.ListField(
        child=serializers.CharField(), source="matched_companions"
    )
    ecosystemHighlights = serializers.ListField(
        child=serializers.CharField(), source="ecosystem_highlights"
    )
    reasoning = serializers.ListField(child=serializers.CharField())
    inpnValidated = serializers.BooleanField(source="inpn_validated")


class FloraRecommendationsSerializer(serializers.Serializer):
    localFloraSummary = LocalFloraSummarySerializer(source="local_flora_summary")
    lczContext = serializers.CharField(source="lcz_context", allow_blank=True)
    lczIndex = serializers.CharField(source="lcz_index", allow_null=True)
    lczDescription = serializers.CharField(source="lcz_description", allow_null=True)
    recommendations = TreeRecommendationSerializer(many=True)
