"""
MVT Generator as django-media.
"""

import math
from concurrent.futures import ThreadPoolExecutor, as_completed
import gc

from django.contrib.gis.db.models import Extent
from django.contrib.gis.geos import Polygon
from django.db.models import QuerySet
from django.contrib.gis.db.models.functions import Intersection
import mercantile
import mapbox_vector_tile
from typing import Dict
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

        Reference:
        https://makina-corpus.com/django/generer-des-tuiles-vectorielles-sur-mesure-avec-django
        """
        # Calculate tile bounds
        tile_bounds = mercantile.xy_bounds(tile)
        west, south, east, north = tile_bounds
        pixel = self.pixel_length(zoom)
        buffer = 4 * pixel

        # Create GeoDjango polygon for tile extent
        tile_polygon = Polygon.from_bbox(
            (west - buffer, south - buffer, east + buffer, north + buffer)
        )
        tile_polygon.srid = TARGET_MAP_PROJ
        # Filter queryset to tile extent and then clip it
        clipped_queryset = self.queryset.filter(
            map_geometry__intersects=tile_polygon
        ).annotate(clipped_geometry=Intersection("map_geometry", tile_polygon))

        if clipped_queryset.exists():
            transformed_geometries = {
                "name": f"{self.geolevel}--{self.datatype}",
                "features": [],
            }

            for lcz in tqdm(
                clipped_queryset,
                desc=f"Processing LCZ features ({tile.x}, {tile.y}, {zoom})",
            ):
                properties = lcz.get_layer_properties()
                if properties["indice"] == "F":
                    continue
                clipped_geom = lcz.clipped_geometry
                transformed_geometries["features"].append(
                    {
                        "geometry": clipped_geom.simplify(
                            pixel, preserve_topology=True
                        ).wkt,
                        "properties": properties,
                    }
                )

            mvt_data = mapbox_vector_tile.encode(
                transformed_geometries, quantize_bounds=(west, south, east, north)
            )

            filename = f"{self.geolevel}/{self.datatype}/{zoom}/{tile.x}/{tile.y}.mvt"
            mvt_tile = MVTTile(
                geolevel=self.geolevel,
                datatype=self.datatype,
                zoom_level=zoom,
                tile_x=tile.x,
                tile_y=tile.y,
            )
            mvt_tile.save_mvt(mvt_data, filename)

    @staticmethod
    def pixel_length(zoom):
        """Width of a pixel in Web Mercator"""
        RADIUS = 6378137
        CIRCUM = 2 * math.pi * RADIUS
        SIZE = 512
        return CIRCUM / SIZE / 2 ** int(zoom)
