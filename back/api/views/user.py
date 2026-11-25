"""Writes coming from users: feedback and short links."""

import logging
import secrets

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Feedback, ShortLink
from api.serializers import FeedbackSerializer
from api.throttling import WriteThrottle

logger = logging.getLogger(__name__)

MAX_PATH_LENGTH = ShortLink._meta.get_field("path").max_length


class FeedbackView(generics.CreateAPIView):
    queryset = Feedback
    serializer_class = FeedbackSerializer
    throttle_classes = [WriteThrottle]

    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        response = self.create(request, *args, **kwargs)

        if response.status_code == status.HTTP_201_CREATED:
            self.send_feedback_email(response.data)

        return response

    def send_feedback_email(self, feedback_data):
        email = feedback_data.get("email", "Anonyme")
        subject = f"Retour utilisateur IA.rbre de {email}"
        created_date = feedback_data["created"]

        email_body = f"""
        # Retour Utilisateur

        **Email**: {email}
        **Date**: {created_date}

        ## Commentaire :
        {feedback_data['feedback']}
        """
        send_mail(
            subject,
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [settings.RECIPIENT_EMAIL],
        )


class ShortLinkCreateView(APIView):
    throttle_classes = [WriteThrottle]

    def post(self, request):
        path = request.data.get("path")
        if (
            not isinstance(path, str)
            or not path.startswith("/")
            or path.startswith("//")
            or len(path) > MAX_PATH_LENGTH
        ):
            return Response(
                {"path": "Invalid path"}, status=status.HTTP_400_BAD_REQUEST
            )
        link = ShortLink.objects.filter(path=path).first()
        if link:
            return Response({"code": link.code}, status=status.HTTP_200_OK)
        link = ShortLink.objects.create(code=secrets.token_urlsafe(6), path=path)
        return Response({"code": link.code}, status=status.HTTP_201_CREATED)


class ShortLinkDetailView(APIView):
    def get(self, request, code):
        link = get_object_or_404(ShortLink, code=code)
        return Response({"path": link.path})
