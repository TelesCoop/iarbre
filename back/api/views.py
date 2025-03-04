import time
import json
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from api.constants import ModelType
from api.map import load_tiles
from typing import Any, Dict

from django.http import JsonResponse
from iarbre_data.models import Feedback

MODEL_BY_TYPE = {
    ModelType.TILE.value: "tile",
}


@require_GET
@cache_page(60 * 60 * 24)
def tile_view(request, model_type, zoom, x, y):
    """View to get tiles for a specific model type.
    Params:
        model_type (str): Type of model to get tiles for.
        zoom (int): Zoom level of the tile.
        x (int): X coordinate of the tile.
        y (int): Y coordinate of the tile.
    Returns:
        HttpResponse: Response containing the MVT tile.
    """
    start_time = time.time()
    model = MODEL_BY_TYPE[model_type]
    response = load_tiles(model, x, y, zoom)
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
