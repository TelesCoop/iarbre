"""OpenAPI schema (drf-spectacular), limited to the public API.

Only ``/api/v1/`` is documented: ``/api/app/`` has no stability guarantee and the
legacy aliases duplicate ``v1`` routes. The WFS view (django-gisserver) is not a
DRF view and is not in the schema, see ``docs/back/api-rest.md``.
"""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, inline_serializer
from rest_framework import serializers

PUBLIC_PREFIX = "/api/v1/"


def public_endpoints_only(endpoints, **kwargs):
    return [endpoint for endpoint in endpoints if endpoint[0].startswith(PUBLIC_PREFIX)]


# Tags, in the order of docs/back/api-rest.md.
TAG_REFERENCE = "Référentiel territorial"
TAG_INDICATORS = "Indicateurs"
TAG_MAP_LAYERS = "Couches cartographiques"
TAG_GEOSERVICES = "Téléchargement et flux SIG"
TAG_METADATA = "Métadonnées"


# --- Reusable pieces --------------------------------------------------------------

LAT_LNG_PARAMETERS = [
    OpenApiParameter("lat", float, required=True, description="Latitude EPSG:4326"),
    OpenApiParameter("lng", float, required=True, description="Longitude EPSG:4326"),
]

ERROR_RESPONSE = OpenApiResponse(
    inline_serializer("Error", {"error": serializers.CharField()}),
    description="Paramètre manquant ou invalide",
)

NOT_FOUND_RESPONSE = OpenApiResponse(description="Objet introuvable")

THROTTLED_RESPONSE = OpenApiResponse(description="Trop de requêtes (throttling par IP)")

GEOJSON_FEATURE_COLLECTION = OpenApiResponse(
    OpenApiTypes.OBJECT, description="GeoJSON FeatureCollection, EPSG:4326"
)

POLYGON_REQUEST = {
    "application/json": {
        "type": "object",
        "description": (
            "Géométrie GeoJSON Polygon en EPSG:4326, 5 km² et 100 sommets maximum."
        ),
        "properties": {
            "type": {"type": "string", "enum": ["Polygon"]},
            "coordinates": {
                "type": "array",
                "items": {
                    "type": "array",
                    "items": {"type": "array", "items": {"type": "number"}},
                },
            },
        },
        "required": ["type", "coordinates"],
        "example": {
            "type": "Polygon",
            "coordinates": [
                [
                    [4.834, 45.759],
                    [4.836, 45.759],
                    [4.836, 45.761],
                    [4.834, 45.761],
                    [4.834, 45.759],
                ]
            ],
        },
    }
}


def binary_response(media_type: str, description: str) -> dict:
    return {
        (200, media_type): OpenApiResponse(OpenApiTypes.BINARY, description=description)
    }
