"""Operations: health check and data metadata."""

import django
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework.views import APIView
from telescoop_backup.backup import FILE_FORMAT, get_backups

from api.constants import ONE_DAY


class HealthCheckView(APIView):
    def get(self, request, *args, **kwargs):
        django.db.connection.ensure_connection()
        return Response("OK")


class MetadataView(APIView):
    @method_decorator(cache_page(ONE_DAY))
    def get(self, request):
        backups = get_backups(date_format=FILE_FORMAT)
        generation_date = backups[-1]["key"]["Key"].split("T")[0][:7]
        return Response(
            {"generation_date": generation_date if generation_date else None}
        )
