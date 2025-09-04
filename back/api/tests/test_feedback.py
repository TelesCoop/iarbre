import json
from django.test import TestCase, Client, override_settings
from api.models import Feedback


@override_settings(RECIPIENT_EMAIL="test@example.com")
class ReceiveFeedbackViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = "/api/feedback/"

    def test_valid_feedback_submission(self):
        data = {
            "email": "molly.maguires@test.fr",
            "feedback": "Raise the floor not the ceiling.",
        }
        response = self.client.post(
            self.url, json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Feedback.objects.filter(
                feedback="Raise the floor not the ceiling."
            ).exists()
        )
        self.assertTrue(
            Feedback.objects.filter(email="molly.maguires@test.fr").exists()
        )

    def test_missing_feedback_field(self):
        data = {"email": "molly.maguires@test.fr"}  # No feedback text
        response = self.client.post(
            self.url, json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

    def test_missing_email_field(self):
        data = {
            "feedback": "Raise the floor not the ceiling."
        }  # Email is not mandatory
        response = self.client.post(
            self.url, json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Feedback.objects.filter(
                feedback="Raise the floor not the ceiling."
            ).exists()
        )

    def test_invalid_json_format(self):
        response = self.client.post(
            self.url, "{invalid_json}", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
