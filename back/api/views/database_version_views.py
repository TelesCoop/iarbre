from telescoop_backup.backup import get_backups, FILE_FORMAT
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class MetadataView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        backups = get_backups(date_format=FILE_FORMAT)
        generation_date = backups[-1]["key"]["Key"].split("T")[0][:7]
        print(generation_date)
        return Response(
            {"generation_date": generation_date if generation_date else None}
        )
