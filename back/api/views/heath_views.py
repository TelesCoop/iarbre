import django
from rest_framework.response import Response
from rest_framework.views import APIView


def _verify_database_connection():
    try:
        connection.ensure_connection()
    finally:
        connection.close()


class HealthCheckView(APIView):
    def get(self, request, *args, **kwargs):
        django.db.connection.ensure_connection()
        return Response("OK")
