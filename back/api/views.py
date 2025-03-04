import time
import json
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET, require_POST

from api.constants import ModelType
from api.map import load_tiles

from django.http import JsonResponse
from api.serializers import FeedbackSerializer

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


@require_POST
def receive_feedback(request):
    """The FeedbackSerialize automatically populates the `id` and `created_at` fields as we only receive
    'feedback' and 'email'.
    """
    data = json.loads(request.body)
    serializer = FeedbackSerializer(data=data)
    print(request)
    print(serializer)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse({"message": "Feedback received successfully!"}, status=201)
    return JsonResponse(serializer.errors, status=400)
