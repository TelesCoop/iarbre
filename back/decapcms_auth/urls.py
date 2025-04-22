from django.urls import path
from rest_framework import routers

from .views import callback, auth

router = routers.DefaultRouter()

urlpatterns = [
    path("auth/", auth),
    path("callback/", callback),
]
