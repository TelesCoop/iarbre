import logging

from django.contrib.gis.geos import Point
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.flora_serializer import FloraRecommendationsSerializer
from api.services.gbif_service import fetch_local_flora
from api.services.inpn_service import validate_species_in_france
from api.services.species_knowledge import TREE_SPECIES_DB, get_tree_recommendations
from iarbre_data.models import Lcz

logger = logging.getLogger(__name__)


class FloraRecommendationsView(APIView):
    """Tree species recommendations based on local flora (GBIF) and LCZ context."""

    @method_decorator(cache_page(60 * 60))
    def get(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")

        if not lat or not lng:
            return Response(
                {"error": "Missing required parameters: lat and lng"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            lat = float(lat)
            lng = float(lng)
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid lat/lng values"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        plantability_score = request.query_params.get("plantability_score")
        if plantability_score is not None:
            try:
                plantability_score = float(plantability_score)
            except (ValueError, TypeError):
                plantability_score = None

        # Find LCZ zone at coordinates (WGS84 -> Lambert 93)
        point = Point(lng, lat, srid=4326)
        point.transform(2154)
        lcz = Lcz.objects.filter(geometry__contains=point).first()

        # Fetch local flora from GBIF
        flora = fetch_local_flora(lat, lng)

        # Validate species against INPN TaxRef
        species_names = [s.scientific_name for s in TREE_SPECIES_DB]
        inpn_results = validate_species_in_france(species_names)

        # Get tree recommendations
        result = get_tree_recommendations(
            flora,
            lcz.lcz_index if lcz else None,
            lcz.details if lcz else None,
            plantability_score=plantability_score,
            inpn_results=inpn_results,
        )
        result["lcz_index"] = lcz.lcz_index if lcz else None
        result["lcz_description"] = lcz.lcz_description if lcz else None

        serializer = FloraRecommendationsSerializer(result)
        return Response(serializer.data)
