from concurrent.futures import ThreadPoolExecutor

from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView


def _verify_database_connection():
    try:
        connection.ensure_connection()
    finally:
        connection.close()


class HealthCheckView(APIView):
    def get(self, request, *args, **kwargs):
        # ensure_connection() must not run on a thread with an event loop.
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(_verify_database_connection).result()
        return Response("OK")
