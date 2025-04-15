# Sveltia CMS / Decap CMS Github Oauth Django Application

Add Github Authentication to DecapCMS through yor Django Application.

## Getting Started

In your `settings.py` :

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
    "SCOPE": "repo,user"
}
```
