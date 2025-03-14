from rest_framework.decorators import api_view
import json

# from django.views.decorators.csrf import csrf_exempt

from typing import Any, Dict

from django.http import JsonResponse
from iarbre_data.models import Feedback


# @csrf_exempt  # Mandatory but not really satisfactory
@api_view(["POST"])
def receive_feedback(request):
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
