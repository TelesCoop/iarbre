import time
import django
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    def get(self, request, *args, **kwargs):
        # make sure connection to database is working
        django.db.connection.ensure_connection()
        # simulate a longer request
        time.sleep(2)
        return Response("OK")
