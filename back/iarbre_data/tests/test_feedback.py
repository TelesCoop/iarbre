import json
from django.test import TestCase, Client
from iarbre_data.models import Feedback


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
        self.assertEqual(response.json()["message"], "Feedback saved!")
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
        self.assertEqual(response.json()["error"], "Feedback is required.")

    def test_missing_email_field(self):
        data = {
            "feedback": "Raise the floor not the ceiling."
        }  # Email is not mandatory
        response = self.client.post(
            self.url, json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["message"], "Feedback saved!")
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
        self.assertEqual(
            response.json()["error"],
            "Expecting property name enclosed in double quotes: line 1 column 2 (char 1)",
        )
