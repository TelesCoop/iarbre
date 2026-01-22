"""
MVT Generator as django-media.
"""

import json
from typing import Dict, Type
import itertools
import math
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
import gc
import geopandas as gpd
import numpy as np
from shapely.geometry import box, Polygon as ShapelyPolygon
from django.contrib.gis.db.models.functions import Intersection
from django.contrib.gis.db.models import Extent
from django.contrib.gis.geos import Polygon, GEOSGeometry
from django.db.models import QuerySet, Model
from shapely.geometry import shape
from tqdm import tqdm
import mercantile
import mapbox_vector_tile
from api.constants import DEFAULT_ZOOM_LEVELS, ZOOM_TO_GRID_SIZE
from iarbre_data.utils.database import load_geodataframe_from_db
from iarbre_data.models import MVTTile, Vulnerability
from iarbre_data.settings import TARGET_MAP_PROJ
from plantability.constants import PLANTABILITY_NORMALIZED
import random


MVT_EXTENT = 4096
ZOOM_AGGREGATE_BREAKPOINT = max(ZOOM_TO_GRID_SIZE.keys())


def partition(list_in, n):
    random.shuffle(list_in)
    return [list_in[i::n] for i in range(n)]


class MVTGeneratorWorker:
    def __init__(
        self,
        queryset: QuerySet,
        geolevel: str = "tile",
        datatype: str = "plantability",
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

    @staticmethod
    def create_grid(zone_polygon, grid_size):
        if isinstance(zone_polygon, gpd.GeoDataFrame):
            zone = zone_polygon
        else:
            if (
                hasattr(zone_polygon, "get")
                and zone_polygon.get("type") == "FeatureCollection"
            ):
                # Extract the first feature's geometry
                geometry = zone_polygon["features"][0]["geometry"]
                zone_polygon = shape(geometry)

            zone = gpd.GeoDataFrame(geometry=[zone_polygon], crs=TARGET_MAP_PROJ)
        minx, miny, maxx, maxy = zone.total_bounds

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
            grid_ids.append(f"{int(x)}_{int(y)}")

        grid_gdf = gpd.GeoDataFrame(
            {"grid_id": grid_ids, "geometry": polygons}, crs=zone.crs
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
            tuple: Contains tile_polygon, tile bounds (west, south, east, north), pixel_size and filename
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

        return tile_polygon, (west, south, east, north), filename

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
        tile_polygon, bounds, filename = self._generate_tile_common(tile, zoom)

        def _compute_plantability_tile_side_lenght(tile_geom):
            coords = list(tile_geom.coords[0])
            point1 = coords[0]
            point2 = coords[1]
            return math.sqrt(
                (point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2
            )

        side_length = _compute_plantability_tile_side_lenght(
            self.queryset.first().geometry
        )

        grid_size = ZOOM_TO_GRID_SIZE.get(zoom, side_length)

        # Filter queryset to MVT tile extent
        base_queryset = self.queryset.filter(map_geometry__intersects=tile_polygon)

        if not base_queryset.exists():
            return

        west, south, east, north = tile_polygon.extent
        mvt_tile = ShapelyPolygon.from_bounds(west, south, east, north)

        all_features = []
        use_batch_processing = zoom < 13 and side_length < 10
        if (
            use_batch_processing
        ):  # Process in batch to avoid OOM with zoom <13 for small tiles
            batch_grid_size = (
                grid_size * 100
            )  # *100 for a balance between mem and speed
            batch_grid = self.create_grid(mvt_tile, batch_grid_size)
            for batch_cell in tqdm(
                batch_grid.itertuples(),
                desc=f"Processing batches for MVT Tile: ({tile.x}, {tile.y}, {zoom})",
            ):
                batch_polygon = batch_cell.geometry
                batch_queryset = base_queryset.filter(
                    map_geometry__intersects=GEOSGeometry(batch_polygon.wkt)
                )
                all_features = self._compute_mvt_features(
                    batch_queryset,
                    batch_polygon,
                    grid_size,
                    all_features,
                    side_length,
                    tile,
                    zoom,
                )

        else:  # Load directly all data for the MVT tile
            all_features = self._compute_mvt_features(
                base_queryset,
                mvt_tile,
                grid_size,
                all_features,
                side_length,
                tile,
                zoom,
            )

        transformed_geometries = {
            "name": f"{self.geolevel}--{self.datatype}",
            "features": all_features,
        }
        # Save the MVT data
        self._save_mvt_data(transformed_geometries, bounds, filename, tile, zoom)

    def _compute_mvt_features(
        self, queryset, mvt_polygon, grid_size, all_features, side_length, tile, zoom
    ):
        if not queryset.exists():
            return all_features
        gdf = load_geodataframe_from_db(
            queryset,
            [
                "plantability_normalized_indice",
                "map_geometry",
                "id",
                "vulnerability_idx_id",
            ],
        )
        mvt_gdf = gpd.GeoDataFrame(geometry=[mvt_polygon], crs=TARGET_MAP_PROJ)
        df_clipped = gpd.clip(gdf, mvt_gdf)

        if len(df_clipped) == 0:
            return all_features

        if zoom <= ZOOM_AGGREGATE_BREAKPOINT and side_length <= 10:
            df_grid_clipped = self._make_grid_aggregate(df_clipped, grid_size)
        else:
            df_grid_clipped = df_clipped

        all_features = self._create_mvt_features_plantability(
            df_grid_clipped, all_features, tile, zoom
        )
        return all_features

    def _make_grid_aggregate(
        self, df_clipped: gpd.GeoDataFrame, grid_size: float
    ) -> gpd.GeoDataFrame:
        """
        Aggregate the plantability indices within a grid.

        Args:
            df_clipped (gpd.GeoDataFrame): The GeoDataFrame containing the clipped geometries.
            grid_size (float): The size of the grid cells.

        Returns:
            gpd.GeoDataFrame: The GeoDataFrame with aggregated plantability indices.
        """
        vuln_ids = [
            getattr(obj, "vulnerability_idx_id", None)
            for obj in df_clipped.itertuples()
            if getattr(obj, "vulnerability_idx_id", None) is not None
            and not (
                isinstance(getattr(obj, "vulnerability_idx_id", None), float)
                and np.isnan(getattr(obj, "vulnerability_idx_id", None))
            )
        ]
        vulnerabilities = Vulnerability.objects.in_bulk(vuln_ids) if vuln_ids else {}

        # Add vulnerability indices to the dataframe
        df_with_vuln = df_clipped.copy()
        df_with_vuln["vulnerability_index_day"] = df_with_vuln.apply(
            lambda row: (
                vulnerabilities[row["vulnerability_idx_id"]].vulnerability_index_day
                if row["vulnerability_idx_id"] in vulnerabilities
                else None
            ),
            axis=1,
        )
        df_with_vuln["vulnerability_index_night"] = df_with_vuln.apply(
            lambda row: (
                vulnerabilities[row["vulnerability_idx_id"]].vulnerability_index_night
                if row["vulnerability_idx_id"] in vulnerabilities
                else None
            ),
            axis=1,
        )

        grid = self.create_grid(df_clipped, grid_size)
        grid = gpd.clip(grid, df_clipped)
        spatial_join = gpd.sjoin(df_with_vuln, grid, how="left", predicate="intersects")

        # Aggregate plantability and vulnerability indices
        aggregated = (
            spatial_join.groupby("grid_id")
            .agg(
                {
                    "plantability_normalized_indice": ["mean", lambda x: list(x)],
                    "vulnerability_index_day": lambda x: (
                        np.nanmean(x.dropna()) if not x.dropna().empty else 5
                    ),
                    "vulnerability_index_night": lambda x: (
                        np.nanmean(x.dropna()) if not x.dropna().empty else 5
                    ),
                }
            )
            .reset_index()
        )

        aggregated.columns = [
            "grid_id",
            "plantability_normalized_indice",
            "source_values",
            "vulnerability_index_day_mean",
            "vulnerability_index_night_mean",
        ]

        # Map the mean values to PLANTABILITY_NORMALIZED set of values
        aggregated["plantability_normalized_indice"] = aggregated[
            "plantability_normalized_indice"
        ].apply(self.map_to_discrete_value)

        aggregated["vulnerability_index_day_mean"] = (
            aggregated["vulnerability_index_day_mean"].fillna(5).round().astype(int)
        )
        aggregated["vulnerability_index_night_mean"] = (
            aggregated["vulnerability_index_night_mean"].fillna(5).round().astype(int)
        )

        # Store source_values in a JSON format to be added in the `details` field
        aggregated["source_values"] = aggregated["source_values"].apply(
            lambda x: json.dumps(x) if x else "[]"
        )

        df_clipped = grid.merge(aggregated, on="grid_id", how="left")
        df_clipped = df_clipped.rename(columns={"grid_id": "id"})
        df_clipped = df_clipped.rename(
            columns={"vulnerability_index_day_mean": "vulnerability_indice_day"}
        )
        df_clipped = df_clipped.rename(
            columns={"vulnerability_index_night_mean": "vulnerability_indice_night"}
        )

        return df_clipped

    @staticmethod
    def _create_mvt_features_plantability(
        df_clipped: gpd.GeoDataFrame,
        all_features: list,
        tile: mercantile.Tile,
        zoom: int,
    ) -> list:
        """
        Create MVT features for plantability.

        Args:
            df_clipped (gpd.GeoDataFrame): The GeoDataFrame containing the clipped geometries.
            all_features (list): The list to append the new features to.
            tile (mercantile.Tile): The tile to generate the MVT for.
            zoom (int): The zoom level of the tile.

        Returns:
            list: The updated list of features with the new MVT features appended.
        """
        if zoom > ZOOM_AGGREGATE_BREAKPOINT:
            # Bulk load vulnerability data, not for aggregated
            vuln_ids = [
                getattr(obj, "vulnerability_idx_id", None)
                for obj in df_clipped.itertuples()
                if getattr(obj, "vulnerability_idx_id", None) is not None
                and not (
                    isinstance(getattr(obj, "vulnerability_idx_id", None), float)
                    and np.isnan(getattr(obj, "vulnerability_idx_id", None))
                )
            ]
            vulnerabilities = (
                Vulnerability.objects.in_bulk(vuln_ids) if vuln_ids else {}
            )
            vuln_props = {
                vuln_id: {
                    k: v for k, v in vuln.get_layer_properties().items() if k != "id"
                }
                for vuln_id, vuln in vulnerabilities.items()
            }

        for obj in tqdm(
            df_clipped.itertuples(),
            desc=f"Processing MVT Tile: ({tile.x}, {tile.y}, {zoom})",
        ):
            properties = {
                "id": obj.id,
                "indice": obj.plantability_normalized_indice,
                "source_values": (
                    obj.source_values if hasattr(obj, "source_values") else []
                ),
            }

            # Add aggregated vulnerability means if available (from grid aggregation)
            if (
                hasattr(obj, "vulnerability_indice_day")
                and obj.vulnerability_indice_day is not None
            ):
                properties["vulnerability_indice_day"] = obj.vulnerability_indice_day
            if (
                hasattr(obj, "vulnerability_indice_night")
                and obj.vulnerability_indice_night is not None
            ):
                properties[
                    "vulnerability_indice_night"
                ] = obj.vulnerability_indice_night
            if zoom > ZOOM_AGGREGATE_BREAKPOINT:
                v_id = getattr(obj, "vulnerability_idx_id", None)
                if v_id:
                    vulnerability_properties = vuln_props.get(v_id, {})
                    for key, value in vulnerability_properties.items():
                        properties[f"vulnerability_{key}"] = value
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
        tile_polygon, bounds, filename = self._generate_tile_common(tile, zoom)

        # Filter queryset to tile extent and then clip it
        clipped_queryset = self.queryset.filter(
            map_geometry__intersects=tile_polygon
        ).annotate(clipped_geometry=Intersection("map_geometry", tile_polygon))

        if len(clipped_queryset) > 0:
            transformed_geometries = {
                "name": f"{self.geolevel}--{self.datatype}",
                "features": [],
            }
            for obj in clipped_queryset:
                properties = obj.get_layer_properties()
                clipped_geom = obj.clipped_geometry
                transformed_geometries["features"].append(
                    {
                        "geometry": clipped_geom.wkt,
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
        """Map value of normalized plantability to normalized plantability set"""
        if x is None:
            return None
        for i in range(1, len(PLANTABILITY_NORMALIZED)):
            if x < PLANTABILITY_NORMALIZED[i]:
                return PLANTABILITY_NORMALIZED[i - 1]
        return PLANTABILITY_NORMALIZED[-1]


class MVTGenerator:
    def __init__(
        self,
        mdl: Type[Model],
        zoom_levels: tuple[int, int] = DEFAULT_ZOOM_LEVELS,
        number_of_workers: int = 1,
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
        self.mdl = mdl
        self.min_zoom, self.max_zoom = zoom_levels
        self.number_of_workers = number_of_workers

    @staticmethod
    def process_tiles(mdl, tiles, number_of_thread):
        mvt_generator = MVTGeneratorWorker(
            mdl.objects.all(), geolevel=mdl.geolevel, datatype=mdl.datatype
        )
        if mvt_generator.datatype == "plantability":
            funct = mvt_generator._generate_tile_for_zoom_plantability
        else:
            funct = mvt_generator._generate_tile_for_zoom

        future_to_tiles = {}
        with ThreadPoolExecutor(max_workers=number_of_thread) as executor:
            for tile, zoom in tiles:
                future_to_tiles[executor.submit(funct, tile, zoom)] = tile

            for future in as_completed(future_to_tiles):
                future.result()
                future_to_tiles.pop(future)  # Free RAM after completion
                gc.collect()
        return len(tiles)

    def generate_tiles(self, ignore_existing=False):
        """Generate MVT tiles for the entire geometry queryset."""
        # Get total bounds of the queryset
        bounds = self._get_queryset_bounds()

        tiles_to_generate = []
        for zoom in range(self.min_zoom, self.max_zoom + 1):
            has_mvt_tiles = (
                MVTTile.objects.filter(
                    geolevel=self.mdl.geolevel,
                    datatype=self.mdl.datatype,
                    zoom_level=zoom,
                ).count()
                > 0
            )
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

            for tile in tiles:
                if ignore_existing or not has_mvt_tiles:
                    tiles_to_generate.append((tile, zoom))
                else:
                    try:
                        MVTTile.objects.get(
                            tile_x=tile.x,
                            tile_y=tile.y,
                            zoom_level=zoom,
                            geolevel=self.mdl.geolevel,
                            datatype=self.mdl.datatype,
                        )
                    except MVTTile.DoesNotExist:
                        tiles_to_generate.append((tile, zoom))

        tiles_to_generate_by_process = partition(
            tiles_to_generate, int(len(tiles_to_generate) / 100)
        )
        futures = []
        progress = 0
        with ProcessPoolExecutor(
            max_workers=self.number_of_workers
        ) as process_executor:
            for tiles in tiles_to_generate_by_process:
                futures.append(
                    process_executor.submit(
                        MVTGenerator.process_tiles,
                        self.mdl,
                        tiles,
                        4,
                    )
                )
                # process_executor.submit(self.process_tiles, funct, tiles, 32)#)
            for future in as_completed(futures):
                future.exception()
                progress += future.result()
                print(
                    f"> Processing MVT Tiles: {progress} / {len(tiles_to_generate)} ({round(progress/len(tiles_to_generate), 2)}%)"
                )
                # futures.pop()
                gc.collect()

    def _get_queryset_bounds(self) -> Dict[str, float]:
        """
        Compute bounds of the entire queryset.

        Returns:
            Dictionary containing the bounds of the queryset.
        """
        # Assumes the queryset has a geographic field
        bbox = self.mdl.objects.all().aggregate(bbox=Extent("map_geometry"))["bbox"]
        bbox_polygon = Polygon.from_bbox(bbox)
        bbox_polygon.srid = TARGET_MAP_PROJ
        bbox_polygon.transform(4326)
        return {
            "west": bbox_polygon.extent[0],
            "south": bbox_polygon.extent[1],
            "east": bbox_polygon.extent[2],
            "north": bbox_polygon.extent[3],
        }
