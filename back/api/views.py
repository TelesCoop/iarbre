import time
import json
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from api.constants import GeoLevel, DataType
from api.map import load_tiles
from typing import Any, Dict

from django.http import JsonResponse
from iarbre_data.models import Feedback

MODEL_BY_TYPE = {
    GeoLevel.TILE.value: "tile",
    GeoLevel.LCZ.value: "lcz",
    "fake_model": "fake_model",  # for the tests
}

LAYER_BY_DATATYPE = {
    DataType.TILE.value: "plantability",
    DataType.LCZ.value: "lcz",
    "fake_layer": "fake_layer",  # for the tests
}


@require_GET
@cache_page(60 * 60 * 24)
def tile_view(
    request, geolevel: str, datatype: str, zoom: int, x: int, y: int
) -> HttpResponse:
    """View to get tiles for a specific model type.

    This view handles GET requests to retrieve tiles for a given model type, zoom level,
    and tile coordinates (x, y).
    Args:
        request (HttpRequest): The HTTP request object.
        geolevel (str): Geolevel to get tiles for.
        datatype (str): Datatype to get tiles for.
        zoom (int): Zoom level of the tile.
        x (int): X coordinate of the tile.
        y (int): Y coordinate of the tile.

    Returns:
        HttpResponse: Response containing the MVT tile.
    """
    start_time = time.time()
    glvl = MODEL_BY_TYPE[geolevel]
    dt = LAYER_BY_DATATYPE[datatype]
    response = load_tiles(glvl, dt, x, y, zoom)
    print(f"Request duration: {time.time() - start_time} seconds")
    return response


@csrf_exempt  # Mandatory but not really satisfactory
@require_POST
def receive_feedback(request) -> JsonResponse:
    """
    Handles feedback submission.

    This view accepts POST requests with JSON data containing feedback.
    The feedback is stored in the database, and a response is returned indicating
    the success or failure of the operation.

    Request JSON format:
    {
        "email": "user@example.com",  # Optional
        "feedback": "User feedback text"
    }
    Returns:
        JsonResponse: A JSON response indicating the result of the feedback submission.
            - On success: {"message": "Feedback saved!", "id": <feedback_id>}
            - On failure: {"error": <error_message>}
    """
    try:
        data: Dict[str, Any] = json.loads(request.body)
        if not data.get("feedback"):  # Email is not mandatory
            return JsonResponse({"error": "Feedback is required."}, status=400)
        feedback = Feedback.objects.create(
            email=data.get("email"),
            feedback=data.get("feedback"),
        )
        return JsonResponse(
            {"message": "Feedback saved!", "id": feedback.id}, status=201
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
