import django
import time
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    def get(self, request, *args, **kwargs):
        django.db.connection.ensure_connection()
        time.sleep(2)
        return Response("OK")
