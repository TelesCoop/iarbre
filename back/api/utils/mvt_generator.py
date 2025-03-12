"""
MVT Generator as django-media.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import gc

from django.contrib.gis.db.models import Extent
from django.contrib.gis.geos import Polygon, MultiPolygon
from django.db.models import QuerySet
from shapely import Polygon as Polygon_shapely
from django.contrib.gis.db.models.functions import Intersection
import mercantile
import mapbox_vector_tile
from typing import List, Dict, Any, Tuple
from iarbre_data.models import MVTTile
from tqdm import tqdm

from iarbre_data.settings import TARGET_MAP_PROJ
from api.constants import DEFAULT_ZOOM_LEVELS

MVT_EXTENT = 4096


class MVTGenerator:
    def __init__(
        self,
        queryset: QuerySet,
        geolevel: str = "tile",
        datatype: str = "plantability",
        zoom_levels: tuple[int, int] = DEFAULT_ZOOM_LEVELS,
        number_of_thread: int = 1,
    ):
        """
        Initialize MVT Generator for Django GeoDjango QuerySet.

        Args:
            queryset (QuerySet): QuerySet of the model.
            geolevel (str): Name of the model to generate MVT tiles for.
            datatype (str): Name of the datatype to generate MVT tiles for.
            zoom_levels (tuple[int, int]): Tuple of minimum and maximum zoom levels to generate tiles for.
            number_of_thread (int): Number of threads to use for generating tiles.
        """
        self.queryset = queryset
        self.datatype = datatype
        self.geolevel = geolevel
        self.min_zoom, self.max_zoom = zoom_levels
        self.number_of_thread = number_of_thread

    def generate_tiles(self):
        """Generate MVT tiles for the entire geometry queryset."""
        # Get total bounds of the queryset
        bounds = self._get_queryset_bounds()
        for zoom in range(self.min_zoom, self.max_zoom + 1):
            print(f"Generating tiles for zoom level {zoom}")
            # Get all tiles that cover the entire geometry bounds
            # bbox needs to be in 4326
            tiles = list(
                mercantile.tiles(
                    bounds["west"],
                    bounds["south"],
                    bounds["east"],
                    bounds["north"],
                    zoom,
                    truncate=True,
                )
            )

            with ThreadPoolExecutor(max_workers=self.number_of_thread) as executor:
                future_to_tiles = {
                    executor.submit(self._generate_tile_for_zoom, tile, zoom): tile
                    for tile in tiles
                }
                for future in as_completed(future_to_tiles):
                    future.result()
                    future_to_tiles.pop(future)  # Free RAM after completion
                    gc.collect()

    def _get_queryset_bounds(self) -> Dict[str, float]:
        """
        Compute bounds of the entire queryset.

        Returns:
            Dictionary containing the bounds of the queryset.
        """
        # Assumes the queryset has a geographic field
        bbox = self.queryset.aggregate(bbox=Extent("map_geometry"))["bbox"]
        bbox_polygon = Polygon.from_bbox(bbox)
        bbox_polygon.srid = TARGET_MAP_PROJ
        bbox_polygon.transform(4326)
        return {
            "west": bbox_polygon.extent[0],
            "south": bbox_polygon.extent[1],
            "east": bbox_polygon.extent[2],
            "north": bbox_polygon.extent[3],
        }

    def _generate_tile_for_zoom(self, tile: mercantile.Tile, zoom: int) -> None:
        """
        Generate an individual MVT tile for the given tile and zoom level.

        Args:
            tile (mercantile.Tile): The tile to generate the MVT for.
            zoom (int): The zoom level of the tile.

        Returns:
            None
        """
        # Calculate tile bounds
        tile_bounds = mercantile.xy_bounds(tile)
        west, south, east, north = tile_bounds

        # Create GeoDjango polygon for tile extent
        tile_polygon = Polygon.from_bbox((west, south, east, north))
        tile_polygon.srid = TARGET_MAP_PROJ
        # Filter queryset to tile extent and then clip it
        clipped_queryset = self.queryset.filter(
            map_geometry__intersects=tile_polygon
        ).annotate(clipped_geometry=Intersection("map_geometry", tile_polygon))

        if clipped_queryset.exists():
            # Prepare MVT features
            features = self._prepare_mvt_features(clipped_queryset, tile_polygon)
            if features:
                # Encode MVT
                mvt_data = mapbox_vector_tile.encode(
                    [
                        {
                            "name": f"{self.geolevel}--{self.datatype}",
                            "features": features,
                        }
                    ]
                )
                filename = (
                    f"{self.geolevel}/{self.datatype}/{zoom}/{tile.x}/{tile.y}.mvt"
                )
                mvt_tile = MVTTile(
                    geolevel=self.geolevel,
                    datatype=self.datatype,
                    zoom_level=zoom,
                    tile_x=tile.x,
                    tile_y=tile.y,
                )
                mvt_tile.save_mvt(mvt_data, filename)

    @staticmethod
    def _prepare_mvt_features(
        queryset: QuerySet, tile_polygon: Polygon
    ) -> List[Dict[str, Any]]:
        """
        Prepare features for MVT encoding.

        Args:
            queryset (QuerySet): Queryset of the model.
            tile_polygon (Polygon): Polygon of the tile extent.

        Returns:
            List of features to encode in MVT format.
        """
        features = []
        (x0, y0, x_max, y_max) = tile_polygon.extent
        x_span = x_max - x0
        y_span = y_max - y0
        for obj in tqdm(queryset, desc="Preparing MVT features", total=len(queryset)):
            clipped_geom = obj.clipped_geometry
            if not clipped_geom.empty:
                if isinstance(clipped_geom, MultiPolygon):
                    clipped_geom_list = list(clipped_geom)
                elif isinstance(clipped_geom, Polygon):
                    clipped_geom_list = [clipped_geom]
                else:
                    raise TypeError("clipped_geom is not MultiPolygon or a Polygon.")
                for clipped in clipped_geom_list:
                    tile_based_coords = MVTGenerator.transform_to_tile_relative(
                        clipped, x0, y0, x_span, y_span
                    )
                    feature = {
                        "geometry": Polygon_shapely(tile_based_coords),
                        "properties": obj.get_layer_properties(),
                    }
                    features.append(feature)

        return features

    @staticmethod
    def transform_to_tile_relative(
        clipped_geom: Polygon, x0: float, y0: float, x_span: float, y_span: float
    ) -> List[Tuple[int, int]]:
        """
        Transform coordinates to relative coordinates within the MVT tile.

        Args:
            clipped_geom (Polygon): The clipped geometry object.
            x0 (float): The minimum x-coordinate of the tile extent.
            y0 (float): The minimum y-coordinate of the tile extent.
            x_span (float): The span of the x-coordinates of the tile extent.
            y_span (float): The span of the y-coordinates of the tile extent.

        Returns:
            List[Tuple[int, int]]: List of transformed coordinates relative to the MVT tile.
        """
        tile_based_coords = []

        coords = clipped_geom.coords[0]

        if (
            len(clipped_geom.coords) == 2
        ):  # Some geometry have too many points and tuple is length 2
            coords = coords + clipped_geom.coords[1]

        for x_merc, y_merc in coords:
            tile_based_coord = (
                int((x_merc - x0) * MVT_EXTENT / x_span),
                int((y_merc - y0) * MVT_EXTENT / y_span),
            )
            tile_based_coords.append(tile_based_coord)

        return tile_based_coords
