from unittest.mock import patch, MagicMock
from django.test import TestCase, Client, override_settings


@override_settings(
    DECAP_CMS_AUTH={
        "OAUTH_CLIENT_ID": "test_client_id",
        "OAUTH_CLIENT_SECRET": "test_client_secret",
        "SCOPE": "user:email",
    }
)
class DecapCMSAuthViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("decapcms_auth.views.OAuth2Session")
    def test_auth_redirects_to_github(self, mock_oauth_session):
        mock_github = MagicMock()
        mock_github.authorization_url.return_value = (
            "https://github.com/login/oauth/authorize",
            "state",
        )
        mock_oauth_session.return_value = mock_github

        response = self.client.get("/cms/auth/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("github.com", response.url)

    @patch("decapcms_auth.views.OAuth2Session")
    def test_callback_success(self, mock_oauth_session):
        mock_github = MagicMock()
        mock_github.fetch_token.return_value = {"access_token": "test_token"}
        mock_oauth_session.return_value = mock_github

        response = self.client.get("/cms/callback/?code=test_code&state=test_state")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test_token")

    @patch("decapcms_auth.views.OAuth2Session")
    def test_callback_handles_exception(self, mock_oauth_session):
        mock_github = MagicMock()
        mock_github.fetch_token.side_effect = Exception("OAuth error")
        mock_oauth_session.return_value = mock_github

        response = self.client.get("/cms/callback/?code=test_code&state=test_state")

        self.assertEqual(response.status_code, 400)
