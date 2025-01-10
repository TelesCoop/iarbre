import os
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.contrib.gis.db.models import Extent
from django.contrib.gis.geos import Polygon
from shapely import Polygon as Polygon_shapely
from django.contrib.gis.db.models.functions import Intersection
import mercantile
import mapbox_vector_tile
from typing import List, Dict, Any
from iarbre_data.models import MVTTile
from tqdm import tqdm


class MVTGenerator:
    def __init__(
        self,
        queryset,
        layer_name="geometries",
        zoom_levels=(0, 14),
        output_dir=None,
        number_of_thread=1,
    ):
        """Initialize MVT Generator for Django GeoDjango QuerySet
        Params:
            queryset (QuerySet): QuerySet of the model.
            layer_name (str): Name of the layer to generate MVT tiles for.
            zoom_levels (tuple): Tuple of zoom levels to generate tiles for.
            output_dir (str): Output directory to save the MVT tiles.
            number_of_thread (int): Number of threads to use for generating tiles.
        """
        self.queryset = queryset
        self.layer_name = layer_name
        self.min_zoom, self.max_zoom = zoom_levels
        self.number_of_thread = number_of_thread

        # Ensure output directory exists
        self.output_dir = output_dir or os.path.join(settings.BASE_DIR, "mvt_tiles")
        os.makedirs(self.output_dir, exist_ok=True)

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
                futures = [
                    executor.submit(self._generate_tile_for_zoom, tile, zoom)
                    for tile in tiles
                ]
                for future in futures:
                    future.result()

    def _get_queryset_bounds(self) -> Dict[str, float]:
        """Calculate bounds of the entire queryset.
        Returns:
            Dictionary containing the bounds of the queryset.
        """
        # Assumes the queryset has a geographic field
        bbox = self.queryset.aggregate(bbox=Extent("map_geometry"))["bbox"]
        bbox_polygon = Polygon.from_bbox(bbox)
        bbox_polygon.srid = 3857
        bbox_polygon.transform(4326)
        return {
            "west": bbox_polygon.extent[0],
            "south": bbox_polygon.extent[1],
            "east": bbox_polygon.extent[2],
            "north": bbox_polygon.extent[3],
        }

    def _generate_tile_for_zoom(self, tile, zoom):
        """Generate an individual MVT tile
        Params:
            tile (mercantile.Tile): Tile to generate MVT for.
            zoom (int): Zoom level of the tile.
        Returns:
            None
        """
        # Calculate tile bounds
        tile_bounds = mercantile.xy_bounds(tile)
        west, south, east, north = tile_bounds

        # Create GeoDjango polygon for tile extent
        tile_polygon = Polygon.from_bbox((west, south, east, north))
        tile_polygon.srid = 3857

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
                    [{"name": self.layer_name, "features": features}]
                )
                filename = f"{self.layer_name}/{zoom}/{tile.x}/{tile.y}.mvt"
                mvt_tile = MVTTile(
                    zoom_level=zoom,
                    tile_x=tile.x,
                    tile_y=tile.y,
                )
                mvt_tile.save_mvt(mvt_data, filename)

    @staticmethod
    def _prepare_mvt_features(queryset, tile_polygon) -> List[Dict[str, Any]]:
        """Prepare features for MVT encoding.
        Params:
            queryset (QuerySet): Queryset of the model.
            tile_polygon (Polygon): Polygon of the tile extent.
        Returns:
            List of features to encode in MVT format.
        """
        MVT_EXTENT = 4096
        features = []
        (x0, y0, x_max, y_max) = tile_polygon.extent
        x_span = x_max - x0
        y_span = y_max - y0
        for obj in tqdm(queryset, desc="Preparing MVT features", total=len(queryset)):
            clipped_geom = obj.clipped_geometry
            if not clipped_geom.empty:
                tile_based_coords = []  # Transform geometry in tile relative coordinate
                for x_merc, y_merc in clipped_geom.coords[0]:
                    tile_based_coord = (
                        int((x_merc - x0) * MVT_EXTENT / x_span),
                        int((y_merc - y0) * MVT_EXTENT / y_span),
                    )
                    tile_based_coords.append(tile_based_coord)
                feature = {
                    "geometry": Polygon_shapely(tile_based_coords),
                    "properties": obj.get_layer_properties(),
                }
                features.append(feature)

        return features
