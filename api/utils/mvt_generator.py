import os
from os import truncate

from django.conf import settings
from django.contrib.gis.db.models import Extent
from django.contrib.gis.geos import Polygon
import mercantile
import mapbox_vector_tile
from typing import List, Dict, Any

from tqdm import tqdm


class MVTGenerator:
    def __init__(
        self, queryset, layer_name="geometries", zoom_levels=(0, 14), output_dir=None
    ):
        """
        Initialize MVT Generator for Django GeoDjango QuerySet

        :param queryset: Django GeoDjango QuerySet
        :param layer_name: Name of the MVT layer
        :param zoom_levels: Tuple of min and max zoom levels to generate
        """
        self.queryset = queryset
        self.layer_name = layer_name
        self.min_zoom, self.max_zoom = zoom_levels

        # Ensure output directory exists
        self.output_dir = output_dir or os.path.join(settings.BASE_DIR, "mvt_tiles")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_tiles(self):
        """
        Generate MVT tiles for the entire geometry queryset
        """
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
                )
            )

            for index, tile in enumerate(tiles):
                print(
                    f"Generating tile {index + 1} of {len(tiles)} for zoom level {zoom}"
                )
                self._generate_tile_for_zoom(tile, zoom)

    def _get_queryset_bounds(self) -> Dict[str, float]:
        """
        Calculate bounds of the entire queryset

        :return: Dictionary with west, south, east, north coordinates
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
        """
        Generate an individual MVT tile

        :param tile: Mercantile tile object
        :param zoom: Current zoom level
        """
        # Calculate tile bounds
        tile_bounds = mercantile.xy_bounds(tile)
        west, south, east, north = tile_bounds

        # Create GeoDjango polygon for tile extent
        tile_polygon = Polygon.from_bbox((west, south, east, north))
        tile_polygon.srid = 3857

        # Filter queryset to tile extent
        clipped_queryset = self.queryset.filter(map_geometry__intersects=tile_polygon)
        print(len(clipped_queryset))

        if clipped_queryset.exists():
            # Prepare MVT features
            features = self._prepare_mvt_features(clipped_queryset, tile_polygon)

            if features:
                # Encode MVT
                mvt_data = mapbox_vector_tile.encode(
                    [{"name": self.layer_name, "features": features}]
                )

                # Create tile directory structure
                tile_path = os.path.join(self.output_dir, str(zoom), str(tile.x))
                os.makedirs(tile_path, exist_ok=True)

                # Save MVT tile
                with open(os.path.join(tile_path, f"{tile.y}.mvt"), "wb") as f:
                    f.write(mvt_data)

    def _prepare_mvt_features(self, queryset, tile_polygon) -> List[Dict[str, Any]]:
        """
        Prepare features for MVT encoding

        :param queryset: Clipped Django QuerySet
        :param tile_polygon: Tile extent polygon
        :return: List of MVT feature dictionaries
        """
        features = []
        for obj in tqdm(queryset, desc="Preparing MVT features", total=len(queryset)):
            # Clip geometry to tile extent
            clipped_geom = obj.map_geometry.intersection(tile_polygon)

            if not clipped_geom.empty:
                feature = {
                    "geometry": clipped_geom.wkt,
                    "properties": obj.get_layer_properties(),
                }
                features.append(feature)

        return features
