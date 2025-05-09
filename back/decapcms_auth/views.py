from requests_oauthlib import OAuth2Session
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponseBadRequest

AUTHORIZATION_BASE_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"
CLIENT_ID = settings.DECAP_CMS_AUTH["OAUTH_CLIENT_ID"]
CLIENT_SECRET = settings.DECAP_CMS_AUTH["OAUTH_CLIENT_SECRET"]
SCOPE = settings.DECAP_CMS_AUTH["SCOPE"]


def auth(request):
    """Redirect to Github auth"""
    github = OAuth2Session(client_id=CLIENT_ID, scope=SCOPE)
    authorization_url, _ = github.authorization_url(AUTHORIZATION_BASE_URL)
    return redirect(authorization_url)


def callback(request):
    """Retrieve access token"""
    state = request.GET.get("state", "")
    try:
        github = OAuth2Session(CLIENT_ID, state=state, scope=SCOPE)
        token = github.fetch_token(
            TOKEN_URL,
            client_secret=CLIENT_SECRET,
            authorization_response=request.get_full_path(),
        )
        content = {"token": token.get("access_token", ""), "provider": "github"}
        return render(request, "decapcms_auth/callback.html", {"content": content})

    except BaseException:
        return HttpResponseBadRequest()
