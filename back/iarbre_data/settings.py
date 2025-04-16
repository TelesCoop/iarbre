"""
Django settings for iarbre_data project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
import sys
from pathlib import Path
import getconf
from django.http import Http404

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "file_data"

IS_LOCAL_DEV = bool(os.environ.get("TELESCOOP_DEV"))
DEBUG = IS_LOCAL_DEV
IS_TESTING = "test" in sys.argv

if IS_LOCAL_DEV:
    config_paths = ["local_settings.conf", "local_settings.ini"]
else:
    config_paths = [os.environ["CONFIG_PATH"]]
config = getconf.ConfigGetter("myproj", config_paths)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
if IS_LOCAL_DEV:
    SECRET_KEY = "django-insecure-@3rjfjbnt85l*c$)j)c55w-!%0ez(v9vu4e=%d@@)pvljpwg)n"
    ALLOWED_HOSTS = ["*"]
else:
    SECRET_KEY = config.getstr("security.secret_key")
    ALLOWED_HOSTS = config.getlist("security.allowed_hosts")

IS_LOCAL_DEV = bool(os.environ.get("TELESCOOP_DEV"))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = IS_LOCAL_DEV


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "iarbre_data",
    "api",
    "plantability",
    "storages",
    "django_extensions",
    "telescoop_backup",
    "rest_framework",
    "decapcms_auth",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Mandatory for Decap CMS Auth
# https://docs.djangoproject.com/en/5.1/ref/middleware/#cross-origin-opener-policy
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

if IS_LOCAL_DEV:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_METHODS = [
        "DELETE",
        "GET",
        "OPTIONS",
        "PATCH",
        "POST",
        "PUT",
    ]
    CSRF_TRUSTED_ORIGINS = ["http://localhost:3000"]
    # INSTALLED_APPS.append("corsheaders")
    # MIDDLEWARE.append("corsheaders.middleware.CorsMiddleware")
    CORS_ALLOW_CREDENTIALS = True

else:
    ROLLBAR = {
        "access_token": config.getstr("bugs.rollbar_access_token"),
        "environment": (
            "development"
            if DEBUG
            else config.getstr("environment.environment", "production")
        ),
        "exception_level_filters": [
            (Http404, "ignored"),
        ],
        "root": BASE_DIR,
    }
    MIDDLEWARE.append("rollbar.contrib.django.middleware.RollbarNotifierMiddleware")
ROOT_URLCONF = "iarbre_data.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "iarbre_data.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": config.getstr("database.name"),
        "USER": config.getstr("database.user"),
        "PASSWORD": config.getstr("database.password"),
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
MEDIA_URL = "media/"

if IS_LOCAL_DEV:
    STATIC_ROOT = BASE_DIR / "collected_static"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
        "external_file_storage": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
    }
    STATIC_ROOT = config.getstr("staticfiles.static_root")
    MEDIA_ROOT = config.getstr("mediafiles.media_root")
    AWS_S3_ACCESS_KEY_ID = config.getstr("external_file_storage.access")
    AWS_S3_SECRET_ACCESS_KEY = config.getstr("external_file_storage.secret")
    AWS_STORAGE_BUCKET_NAME = config.getstr("external_file_storage.bucket")
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_S3_REGION_NAME = config.getstr("external_file_storage.region")
    AWS_S3_HOST = config.getstr("external_file_storage.host")
    AWS_S3_ENDPOINT_URL = "https://{}".format(AWS_S3_HOST)
    MEDIA_LOCATION = "public-media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Script variables
TARGET_PROJ = 2154  # Lambert 93
TARGET_MAP_PROJ = 3857  # Pseudo-Mercator
BUFFER_SIZE = 2  # meters

# telescoop-backup
BACKUP_ACCESS = config.getstr("backup.backup_access", None)  # S3 ACCESS
BACKUP_SECRET = config.getstr("backup.backup_secret", None)  # S3 SECRET KEY
BACKUP_BUCKET = config.getstr("backup.backup_bucket", None)  # S3 Bucket
BACKUP_HOST = config.getstr("backup.backup_host", None)

BACKUP_COMPRESS = config.getbool("backup.backup_compress", False)
BACKUP_RECOVER_N_WORKERS = config.getint("backup.backup_recovery_n_workers", 1)

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
        "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ),
}

DECAP_CMS_AUTH = {
    "OAUTH_CLIENT_ID": config.getstr("github_oauth.client_id"),
    "OAUTH_CLIENT_SECRET": config.getstr("github_oauth.client_secret"),
    "SCOPE": "repo,user",
}

# For macOS users, we need to set the GDAL_LIBRARY_PATH and GEOS_LIBRARY_PATH to the path of the libraries
if sys.platform == "darwin":
    GDAL_LIBRARY_PATH = os.environ.get("GDAL_LIBRARY_PATH")
    GEOS_LIBRARY_PATH = os.environ.get("GEOS_LIBRARY_PATH")
