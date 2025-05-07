from rest_framework import generics, status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
import requests

from api.models import Feedback
from api.serializers import FeedbackSerializer

from iarbre_data.settings import GITHUB_ISSUES


class FeedbackView(generics.CreateAPIView):
    queryset = Feedback
    serializer_class = FeedbackSerializer

    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        response = self.create(request, *args, **kwargs)

        if response.status_code == status.HTTP_201_CREATED:
            self.create_github_issue(response.data)

        return response

    def create_github_issue(self, feedback_data):
        """Create a GitHub issue based on feedback data."""
        # GitHub API settings
        github_token = GITHUB_ISSUES["token"]
        url = "https://api.github.com/repos/TelesCoop/iarbre/issues"

        email = feedback_data.get("email", "Anonymous")
        issue_title = f"New Feedback from {email}"
        created_date = feedback_data["created"]

        issue_body = f"""
        ## Feedback Utilisateur

        **Email**: {email}
        **Date**: {created_date}

        ### Feedback Content
        {feedback_data['feedback']}
        """

        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        issue_data = {
            "title": issue_title,
            "body": issue_body,
            "labels": ["feedback", "user-submitted"],
        }
        try:
            response = requests.post(url, headers=headers, json=issue_data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error creating GitHub issue: {str(e)}")
