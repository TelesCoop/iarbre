# Sveltia CMS / Decap CMS Github Oauth Django Application

Add Github Authentication to DecapCMS through yor Django Application.

## Getting Started

### 1. Create and register your Github OAuth Application

Please read [official doc](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app).

Authorization callback URL should be :

```
https://<your application url>/callback
```

Copy-paste application id and client secret.

### 2. Install Decap CMS in your Django Project

#### `settings.py` :

- Install application :

```py
INSTALLED_APPS = [
    ...,
    "decapcms_auth",
]
```

- Set up required variables :

```py

DECAP_CMS_AUTH = {
    "OAUTH_CLIENT_ID": "<public application client id>",
    "OAUTH_CLIENT_SECRET": "<private application client secret>"
    "SCOPE": "repo,user"
}
```

⚠️ `OAUTH_CLIENT_SECRET` should not be publicly disclosed.

- Define this environment variable:

```py
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
```

#### `urls.py`

Include the Decap CMS urls :

```py

from decapcms_auth import urls as decapcmsauth_urls
...
urlpatterns = [
    ...
    path("cms/", include(decapcmsauth_urls)),
    ...
]
```

### 3. In your Decap CMS config.yml

```yml
backend:
  name: github
  branch: main
  repo: <your repo>
  base_url: <base url of your application>
  auth_endpoint: /cms/auth # /cms
```
