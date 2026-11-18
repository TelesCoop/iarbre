"""API views, grouped by usage.

- tiles:       map tiles served by z/x/y (MVT, raster PNG, orthophoto proxy)
- spatial:     feature details, values at a point, aggregates in an area
- reference:   administrative divisions and other reference layers
- geoservices: OGC services (WFS, WMS)
- exports:     file downloads and PDF reports
- user:        user writes (feedback, short links)
- system:      health check and metadata
"""

from .exports import (  # noqa: F401
    DashboardExportPdfView,
    DashboardExportScopeView,
    RasterDownloadView,
)
from .geoservices import IArbreWFSView, IArbreWMSView  # noqa: F401
from .reference import (  # noqa: F401
    CityBoundaryView,
    CityView,
    IrisView,
    PublicBuildingListView,
    QPVListView,
)
from .spatial import (  # noqa: F401
    BiosphereLandCoverAtPointView,
    DashboardPolygonView,
    DashboardView,
    ScoresInPolygonView,
    TileDetailsView,
    VegetationHeightAtPointView,
)
from .system import HealthCheckView, MetadataView  # noqa: F401
from .tiles import (  # noqa: F401
    OrthophotoTileView,
    PetTileView,
    ShadowTileView,
    TileView,
    VegetationHeightTileView,
)
from .user import FeedbackView, ShortLinkCreateView, ShortLinkDetailView  # noqa: F401
