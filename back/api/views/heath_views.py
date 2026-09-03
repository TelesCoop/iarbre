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
        # ensure_connection() is async-unsafe and raises as soon as an event loop
        # runs on the request thread; a worker thread never has one.
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(_verify_database_connection).result()
        return Response("OK")
