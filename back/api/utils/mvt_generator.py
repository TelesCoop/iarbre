"""
MVT Generator as django-media.
"""

from typing import Dict
import itertools
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
import gc
import geopandas as gpd
import numpy as np
from shapely.geometry import box, Polygon as ShapelyPolygon
from django.contrib.gis.db.models.functions import Intersection
from django.contrib.gis.db.models import Extent
from django.contrib.gis.geos import Polygon, GEOSGeometry
from django.db.models import QuerySet
from tqdm import tqdm
import mercantile
import mapbox_vector_tile
from api.constants import DEFAULT_ZOOM_LEVELS, ZOOM_TO_GRID_SIZE
from iarbre_data.utils.database import load_geodataframe_from_db
from iarbre_data.models import MVTTile, get_tile_color
from iarbre_data.settings import TARGET_MAP_PROJ
from plantability.constants import PLANTABILITY_NORMALIZED

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
            if self.datatype == "plantability":
                funct = self._generate_tile_for_zoom_plantability
            else:
                funct = self._generate_tile_for_zoom
            with ThreadPoolExecutor(max_workers=self.number_of_thread) as executor:
                future_to_tiles = {
                    executor.submit(funct, tile, zoom): tile
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

    @staticmethod
    def create_grid(gdf, grid_size):
        minx, miny, maxx, maxy = gdf.total_bounds

        minx = np.floor(minx / grid_size) * grid_size
        miny = np.floor(miny / grid_size) * grid_size
        maxx = np.ceil(maxx / grid_size) * grid_size
        maxy = np.ceil(maxy / grid_size) * grid_size

        rows = np.arange(miny, maxy, grid_size)
        cols = np.arange(minx, maxx, grid_size)

        polygons = []
        grid_ids = []
        for (row_idx, y), (col_idx, x) in itertools.product(
            enumerate(rows), enumerate(cols)
        ):
            polygons.append(box(x, y, x + grid_size, y + grid_size))
            grid_ids.append(f"{col_idx}_{row_idx}")

        grid_gdf = gpd.GeoDataFrame(
            {"grid_id": grid_ids, "geometry": polygons}, crs=gdf.crs
        )
        return grid_gdf

    def _generate_tile_common(
        self, tile: mercantile.Tile, zoom: int
    ) -> tuple[Polygon, tuple[float, float, float, float], float, str]:
        """
        Common setup for tile generation that's shared across different datatypes.

        Args:
            tile (mercantile.Tile): The tile to generate the MVT for.
            zoom (int): The zoom level of the tile.

        Returns:
            tuple: Contains tile_polygon, tile bounds (west, south, east, north), pixel size, and filename
        """
        # Compute tile bounds
        tile_bounds = mercantile.xy_bounds(tile)
        west, south, east, north = tile_bounds
        pixel = self.pixel_length(zoom)
        buffer = 4 * pixel

        # Create GeoDjango polygon for tile extent
        tile_polygon = Polygon.from_bbox(
            (west - buffer, south - buffer, east + buffer, north + buffer)
        )
        tile_polygon.srid = TARGET_MAP_PROJ

        filename = f"{self.geolevel}/{self.datatype}/{zoom}/{tile.x}/{tile.y}.mvt"

        return tile_polygon, (west, south, east, north), pixel, filename

    def _save_mvt_data(
        self,
        transformed_geometries: Dict[str, list],
        bounds: tuple[float, float, float, float],
        filename: str,
        tile: mercantile.Tile,
        zoom: int,
    ) -> None:
        """
        Encode and save MVT data.

        Args:
            transformed_geometries (Dict[str, list]): The geometries to encode
            bounds (tuple[float, float, float, float]): The bounds to use for quantization (west, south, east, north)
            filename (str): The filename to save the MVT to
            tile (mercantile.Tile): The tile object
            zoom (int): The zoom level

        Returns:
            None
        """
        west, south, east, north = bounds

        mvt_data = mapbox_vector_tile.encode(
            transformed_geometries, quantize_bounds=(west, south, east, north)
        )

        mvt_tile = MVTTile(
            geolevel=self.geolevel,
            datatype=self.datatype,
            zoom_level=zoom,
            tile_x=tile.x,
            tile_y=tile.y,
        )

        mvt_tile.save_mvt(mvt_data, filename)

    def _generate_tile_for_zoom_plantability(
        self, tile: mercantile.Tile, zoom: int
    ) -> None:
        """
        Generate an individual MVT tile for the given tile and zoom level, only for plantability.

        Args:
            tile (mercantile.Tile): The tile to generate the MVT for.
            zoom (int): The zoom level of the tile.

        Returns:
            None
        """
        # Get common tile data for MapLibre
        tile_polygon, bounds, pixel, filename = self._generate_tile_common(tile, zoom)

        # Compute side length of plantability tile
        geom = self.queryset.first().geometry
        coords = list(geom.coords[0])
        point1 = coords[0]
        point2 = coords[1]
        side_length = math.sqrt(
            (point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2
        )

        grid_size = ZOOM_TO_GRID_SIZE.get(zoom, side_length)

        # Filter queryset to MVT tile extent
        base_queryset = self.queryset.filter(map_geometry__intersects=tile_polygon)
        if base_queryset.exists():
            west, south, east, north = tile_polygon.extent
            mvt_tile = ShapelyPolygon.from_bounds(west, south, east, north)
            clip_mvt_gdf = gpd.GeoDataFrame(geometry=[mvt_tile], crs=TARGET_MAP_PROJ)
            all_features = []
            if (
                zoom < 13 and side_length < 10
            ):  # Process in batch to avoid OOM with zoom <13
                batch_grid_size = grid_size * 100
                batch_grid = self.create_grid(clip_mvt_gdf, batch_grid_size)
                for batch_cell in tqdm(
                    batch_grid.itertuples(),
                    desc=f"Processing batches for MVT Tile: ({tile.x}, {tile.y}, {zoom})",
                ):
                    batch_polygon = batch_cell.geometry
                    batch_queryset = base_queryset.filter(
                        map_geometry__intersects=GEOSGeometry(batch_polygon.wkt)
                    )
                    if not batch_queryset.exists():
                        continue
                    batch_df = load_geodataframe_from_db(
                        batch_queryset,
                        ["plantability_normalized_indice", "map_geometry"],
                    )
                    batch_clip_gdf = gpd.GeoDataFrame(
                        geometry=[batch_polygon], crs=TARGET_MAP_PROJ
                    )
                    batch_df_clipped = gpd.clip(batch_df, batch_clip_gdf)

                    if len(batch_df_clipped) == 0:
                        continue

                    df_grid_clipped = self._make_grid_aggregate(
                        batch_df_clipped, grid_size
                    )
                    all_features = self._create_mvt_features(
                        df_grid_clipped, all_features, tile, zoom
                    )

            else:  # Load directly all data for the MVT tile
                df = load_geodataframe_from_db(
                    base_queryset,
                    ["plantability_normalized_indice", "map_geometry", "id"],
                )
                df_clipped = gpd.clip(df, clip_mvt_gdf)
                if zoom <= 15 and side_length < 10:
                    df_grid_clipped = self._make_grid_aggregate(df_clipped, grid_size)
                else:
                    df_grid_clipped = df_clipped

                all_features = self._create_mvt_features(
                    df_grid_clipped, all_features, tile, zoom
                )

            transformed_geometries = {
                "name": f"{self.geolevel}--{self.datatype}",
                "features": all_features,
            }
            # Save the MVT data
            self._save_mvt_data(transformed_geometries, bounds, filename, tile, zoom)

    def _make_grid_aggregate(self, df_clipped, grid_size):
        grid = self.create_grid(df_clipped, grid_size)
        grid = gpd.clip(grid, df_clipped)
        spatial_join = gpd.sjoin(df_clipped, grid, how="left", predicate="intersects")
        aggregated = (
            spatial_join.groupby("grid_id")["plantability_normalized_indice"]
            .mean()
            .reset_index()
        )
        # Map the mean values to PLANTABILITY_NORMALIZED set
        aggregated["plantability_normalized_indice"] = aggregated[
            "plantability_normalized_indice"
        ].apply(self.map_to_discrete_value)

        df_clipped = grid.merge(aggregated, on="grid_id", how="left")
        df_clipped = df_clipped.rename(columns={"grid_id": "id"})

        return df_clipped

    @staticmethod
    def _create_mvt_features(df_grid_clipped, all_features, tile, zoom):
        for obj in tqdm(
            df_grid_clipped.itertuples(),
            desc=f"Processing MVT Tile: ({tile.x}, {tile.y}, {zoom})",
        ):
            properties = {
                "id": obj.id,
                "indice": obj.plantability_normalized_indice,
                "color": get_tile_color(obj.plantability_normalized_indice),
            }
            all_features.append(
                {
                    "geometry": obj.geometry.wkt,
                    "properties": properties,
                }
            )
        return all_features

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
        # Get common tile data
        tile_polygon, bounds, pixel, filename = self._generate_tile_common(tile, zoom)

        # Filter queryset to tile extent and then clip it
        clipped_queryset = self.queryset.filter(
            map_geometry__intersects=tile_polygon
        ).annotate(clipped_geometry=Intersection("map_geometry", tile_polygon))

        if clipped_queryset.exists():
            transformed_geometries = {
                "name": f"{self.geolevel}--{self.datatype}",
                "features": [],
            }

            for obj in tqdm(
                clipped_queryset,
                desc=f"Processing MVT Tile: ({tile.x}, {tile.y}, {zoom})",
            ):
                properties = obj.get_layer_properties()
                clipped_geom = obj.clipped_geometry
                transformed_geometries["features"].append(
                    {
                        "geometry": clipped_geom.make_valid()
                        .simplify(pixel, preserve_topology=True)
                        .wkt,
                        "properties": properties,
                    }
                )

            # Save the MVT data
            self._save_mvt_data(transformed_geometries, bounds, filename, tile, zoom)

    @staticmethod
    def pixel_length(zoom):
        """Width of a pixel in Web Mercator"""
        RADIUS = 6378137
        CIRCUM = 2 * math.pi * RADIUS
        SIZE = 512
        return CIRCUM / SIZE / 2 ** int(zoom)

    @staticmethod
    def map_to_discrete_value(x):
        """Map average value of normalized plantability to normalized plantability set"""
        if x is None:
            return None
        for i in range(1, len(PLANTABILITY_NORMALIZED)):
            if x < PLANTABILITY_NORMALIZED[i]:
                return PLANTABILITY_NORMALIZED[i - 1]
        return PLANTABILITY_NORMALIZED[-1]
