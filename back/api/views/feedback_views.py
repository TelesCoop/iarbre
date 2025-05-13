from rest_framework import generics, status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
import requests

from api.models import Feedback
from api.serializers import FeedbackSerializer

from iarbre_data.settings import MAILGUN


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
        """Send feedback data via email using Mailgun."""
        MAILGUN_API_KEY = MAILGUN["API_KEY"]
        MAILGUN_DOMAIN = MAILGUN["DOMAIN"]
        RECIPIENT_EMAIL = "Ludovic Telescoop <ludovic@telescoop.fr>"

        email = feedback_data.get("email", "Anonyme")
        subject = f"Feedback IA.rbre de {email}"
        created_date = feedback_data["created"]

        email_body = f"""
        ## Feedback Utilisateur

        **Email**: {email}
        **Date**: {created_date}

        ### Feedback
        {feedback_data['feedback']}
        """
        try:
            response = requests.post(
                f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
                auth=("api", f"key-{MAILGUN_API_KEY}"),
                data={
                    "from": f"Feedback IArbre <postmaster@{MAILGUN_DOMAIN}>",
                    "to": RECIPIENT_EMAIL,
                    "subject": subject,
                    "text": email_body,
                },
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error sending feedback email: {str(e)}")
