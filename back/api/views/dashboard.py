"""Dashboard: aggregated indicators for a division or a polygon, and PDF report."""

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.dashboard_serializer import DashboardSerializer
from api.services.dashboard import (
    aggregate_plantability,
    aggregate_plantability_from_polygon,
    assemble_dashboard_data,
    division_scope,
    polygon_scope,
)
from api.services.pdf_report import (
    PdfExportTimeout,
    get_export_scope,
    render_dashboard_pdf,
    store_export_scope,
)
from api.services.polygon import InvalidPolygon, parse_polygon
from iarbre_data.models import City, Iris


# --- Data -------------------------------------------------------------------------


def _dashboard_response(data: dict) -> Response:
    serializer = DashboardSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.data)


class DashboardView(APIView):
    """Aggregated dashboard data for the metropole, a city, or an IRIS zone.

    GET /api/dashboard/                        -> metropole (all cities)
    GET /api/dashboard/?city_code=69123        -> single city
    GET /api/dashboard/?iris_code=691230101    -> single IRIS
    """

    @method_decorator(cache_page(60 * 60))
    def get(self, request, *args, **kwargs):
        city_code = request.query_params.get("city_code")
        iris_code = request.query_params.get("iris_code")

        city, iris = None, None
        if iris_code:
            iris = get_object_or_404(
                Iris.objects.select_related("city"), code=iris_code
            )
            city = iris.city
        elif city_code:
            city = get_object_or_404(City, code=city_code)

        scope = division_scope(city, iris)
        return _dashboard_response(
            assemble_dashboard_data(scope, aggregate_plantability(scope))
        )


class DashboardPolygonView(APIView):
    """Aggregated dashboard data for a user-drawn polygon.

    POST /api/dashboard/in-polygon/   body: GeoJSON Polygon
    """

    def post(self, request, *args, **kwargs):
        try:
            polygon = parse_polygon(request.data)
        except InvalidPolygon as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return _dashboard_response(
            assemble_dashboard_data(
                polygon_scope(polygon), aggregate_plantability_from_polygon(polygon)
            )
        )


# --- PDF report -------------------------------------------------------------------


class DashboardExportScopeView(APIView):
    """Scope of a pending PDF export, read back by the headless browser."""

    def get(self, request, token, *args, **kwargs):
        scope = get_export_scope(token)
        if scope is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(scope)


class DashboardExportPdfView(APIView):
    def post(self, request, *args, **kwargs):
        token = store_export_scope(request.data)
        frontend_url = settings.PDF_EXPORT_FRONTEND_URL or request.build_absolute_uri(
            "/"
        ).rstrip("/")
        try:
            pdf_bytes = render_dashboard_pdf(token, frontend_url)
        except PdfExportTimeout:
            return Response(
                {"detail": "PDF generation timed out"},
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="rapport.pdf"'
        return response
