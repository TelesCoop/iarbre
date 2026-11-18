"""API views, grouped by usage.

Layers are grouped by kind of endpoint; a self-contained feature with its own
service (the dashboard) gets its own module.

- tiles:       map tiles served by z/x/y (MVT, raster PNG, orthophoto proxy)
- spatial:     feature details, values at a point, scores in an area
- reference:   administrative divisions and other reference layers
- geoservices: geodata distribution (WFS, WMS, raw raster downloads)
- dashboard:   aggregated indicators and PDF report
- user:        user writes (feedback, short links)
- system:      health check and metadata
"""

from .dashboard import (  # noqa: F401
    DashboardExportPdfView,
    DashboardExportScopeView,
    DashboardPolygonView,
    DashboardView,
)
from .geoservices import IArbreWFSView, IArbreWMSView, RasterDownloadView  # noqa: F401
from .reference import (  # noqa: F401
    CityBoundaryView,
    CityView,
    IrisView,
    PublicBuildingListView,
    QPVListView,
)
from .spatial import (  # noqa: F401
    BiosphereLandCoverAtPointView,
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
