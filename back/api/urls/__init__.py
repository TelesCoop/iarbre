"""API routes, mounted on ``/api/``.

- ``v1/``: public API (``public.py``), stable contract for third parties.
- ``app/``: internal API (``app.py``), serves the frontend only.
- ``health-check/``: ops, used by the deployment.
- Legacy aliases: URLs published before ``v1/`` existed, kept so that saved QGIS
  projects and shared download links keep working. Same views, no redirect (OGC
  clients follow redirects poorly). Unnamed so that ``reverse`` gives ``v1/`` URLs.
"""

from django.urls import path, include

from api.views import (
    HealthCheckView,
    IArbreWFSView,
    IArbreWMSView,
    RasterDownloadView,
)

urlpatterns = [
    path("v1/", include("api.urls.public")),
    path("app/", include("api.urls.app")),
    path("health-check/", HealthCheckView.as_view(), name="health-check"),
    # --- legacy aliases -------------------------------------------------------------
    path("wfs/", IArbreWFSView.as_view()),
    path("wms/", IArbreWMSView.as_view()),
    path("rasters/<str:raster_type>/", RasterDownloadView.as_view()),
]
