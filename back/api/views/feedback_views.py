import logging

from rest_framework import generics, status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.mail import send_mail

from api.models import Feedback
from api.serializers import FeedbackSerializer

from django.conf import settings

logger = logging.getLogger(__name__)


class FeedbackView(generics.CreateAPIView):
    queryset = Feedback
    serializer_class = FeedbackSerializer

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
