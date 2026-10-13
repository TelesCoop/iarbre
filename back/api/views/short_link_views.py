import secrets

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from api.models import ShortLink

MAX_PATH_LENGTH = ShortLink._meta.get_field("path").max_length


class ShortLinkCreateView(APIView):
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        path = request.data.get("path")
        if (
            not isinstance(path, str)
            or not path.startswith("/")
            or path.startswith("//")
            or len(path) > MAX_PATH_LENGTH
        ):
            return Response(
                {"path": "Invalid path"}, status=status.HTTP_400_BAD_REQUEST
            )
        link = ShortLink.objects.filter(path=path).first()
        if link:
            return Response({"code": link.code}, status=status.HTTP_200_OK)
        link = ShortLink.objects.create(code=secrets.token_urlsafe(6), path=path)
        return Response({"code": link.code}, status=status.HTTP_201_CREATED)


class ShortLinkDetailView(APIView):
    def get(self, request, code):
        link = get_object_or_404(ShortLink, code=code)
        return Response({"path": link.path})
