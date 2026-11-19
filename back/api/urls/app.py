"""Internal API, mounted on ``/api/app/``.

Routes serving the iarbre frontend only: no stability guarantee, not open to
other origins. Anything useful to third parties belongs in ``public.py``.
"""

from django.urls import path

from api.views import (
    DashboardExportPdfView,
    DashboardExportScopeView,
    FeedbackView,
    OrthophotoTileView,
    PetTileView,
    ShadowTileView,
    ShortLinkCreateView,
    ShortLinkDetailView,
    TileDetailsView,
)

urlpatterns = [
    # --- tiles ----------------------------------------------------------------------
    # Experimental hourly rasters, to move to the public API once stable.
    path(
        "tiles/pet/<int:z>/<int:x>/<int:y>.png",
        PetTileView.as_view(),
        name="pet-tile",
    ),
    path(
        "tiles/shadow/<int:z>/<int:x>/<int:y>.png",
        ShadowTileView.as_view(),
        name="shadow-tile",
    ),
    # Proxy of the Grand Lyon WMS: third parties should use the source.
    path(
        "orthophoto/<int:z>/<int:x>/<int:y>.png",
        OrthophotoTileView.as_view(),
        name="orthophoto-tile",
    ),
    # --- spatial --------------------------------------------------------------------
    # ``id`` is a database key that changes on every data import.
    path(
        "tiles/<datatype>/<id>/",
        TileDetailsView.as_view(),
        name="retrieve-tile-details",
    ),
    # --- dashboard ------------------------------------------------------------------
    path(
        "dashboard/export-scope/<str:token>/",
        DashboardExportScopeView.as_view(),
        name="dashboard-export-scope",
    ),
    path(
        "dashboard/export-pdf/",
        DashboardExportPdfView.as_view(),
        name="dashboard-export-pdf",
    ),
    # --- user -----------------------------------------------------------------------
    path("feedback/", FeedbackView.as_view(), name="create-feedback"),
    path("short-links/", ShortLinkCreateView.as_view(), name="create-short-link"),
    path(
        "short-links/<str:code>/",
        ShortLinkDetailView.as_view(),
        name="retrieve-short-link",
    ),
]
