from rest_framework import generics
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from api.models import Feedback
from api.serializers import FeedbackSerializer


class FeedbackView(generics.CreateAPIView):
    queryset = Feedback
    serializer_class = FeedbackSerializer

    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
