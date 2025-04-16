"""
MVT Generator as django-media.
"""

import math
from concurrent.futures import ThreadPoolExecutor, as_completed
import gc

from django.contrib.gis.db.models import Extent, Union
from django.contrib.gis.geos import Polygon
from django.db.models import QuerySet
from django.contrib.gis.db.models.functions import SnapToGrid
from django.db.models import Avg
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

    def generate_tiles(self, ignore_existing=False):
        """Generate MVT tiles for the entire geometry queryset."""
        # Get total bounds of the queryset
        bounds = self._get_queryset_bounds()
        for zoom in range(self.min_zoom, self.max_zoom + 1):
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
                    if not ignore_existing
                    or MVTTile.objects.filter(
                        tile_x=tile.x,
                        tile_y=tile.y,
                        zoom_level=zoom,
                        geolevel=self.geolevel,
                        datatype=self.datatype,
                    ).count()
                    == 0
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

        if zoom in [11, 12]:
            grid_size = 200
        elif zoom == 13:
            grid_size = 50
        elif zoom == 14:
            grid_size = 20
        elif zoom == 15:
            grid_size = 10

        # Filter queryset to tile extent
        base_queryset = self.queryset.filter(map_geometry__intersects=tile_polygon)

        if base_queryset.exists():
            # Use Django SnapGrid to create a bigger grid and aggregate geometries
            aggregated_geometries = (
                base_queryset.annotate(
                    grid_cell=SnapToGrid("map_geometry", grid_size, grid_size)
                )
                .values("grid_cell")
                .annotate(
                    union_geom=Union("map_geometry"),
                    # Compute average of plantability_normalized_indice
                    avg_indice=Avg("plantability_normalized_indice"),
                )
            )
            for agg in tqdm(
                aggregated_geometries,
                desc=f"Processing MVT Tile: ({tile.x}, {tile.y}, {zoom})",
            ):
                transformed_geometries = {
                    "name": f"{self.geolevel}--{self.datatype}",
                    "features": [],
                }

                union_geom = agg["union_geom"]
                clipped_geom = union_geom.intersection(
                    tile_polygon
                ).envelope  # clip it to polygon extend
                # Determine color based on average indice
                avg_indice = agg["avg_indice"]
                color = self._get_color_for_indice(avg_indice)

                # Create properties for the aggregated geometry
                properties = {
                    "id": f"grid_{tile.x}_{tile.y}_{zoom}_{hash(str(agg['grid_cell']))}",
                    "indice": avg_indice,
                    "color": color,
                }

                transformed_geometries["features"].append(
                    {
                        "geometry": clipped_geom.make_valid()
                        .simplify(pixel, preserve_topology=True)
                        .wkt,
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
    def _get_color_for_indice(indice):
        """Return the color based on the normalized indice."""
        if indice is None:
            return "purple"
        elif indice < 2:  # river indice is about -3, we want gray scale
            return "#E0E0E0"
        elif indice < 4:
            return "#F0F1C0"
        elif indice < 6:
            return "#E5E09A"
        elif indice < 8:
            return "#B7D990"
        elif indice < 10:
            return "#71BB72"
        else:
            return "#006837"

    @staticmethod
    def pixel_length(zoom):
        """Width of a pixel in Web Mercator"""
        RADIUS = 6378137
        CIRCUM = 2 * math.pi * RADIUS
        SIZE = 512
        return CIRCUM / SIZE / 2 ** int(zoom)
