"""Create a grid over the metropole or a selection of city and save it to DB."""

import logging
from tqdm import tqdm
from iarbre_data.models import Iris, Tile, City
import numpy as np
import itertools
from iarbre_data.settings import TARGET_PROJ, TARGET_MAP_PROJ
from pyproj import Transformer
from django.contrib.gis.geos import Polygon
from django.contrib.gis.gdal import DataSource
from typing import Optional, Type
from django.db import transaction
import gc
from shapely.geometry import box

SIN_60 = np.sin(
    np.pi / 3
)  # The height ratio of equilateral triangles forming the hexagon

TRANSFORMATION = Transformer.from_crs("EPSG:2154", "EPSG:3857")


class TileShape:
    @staticmethod
    def get_iris_id(polygon):
        iris_id = Iris.objects.filter(geometry__intersects=polygon)
        if iris_id:
            return iris_id[0].id
        return None


class HexTileShape(TileShape):
    """Generate hexagonal tile."""

    @staticmethod
    def adjust_bounds(xmin, ymin, xmax, ymax, grid_size, side_length):
        """Snap bounds to the nearest grid alignment."""
        hex_width = 3 * side_length
        hex_height = 2 * side_length * SIN_60
        xmin = hex_width * np.floor(xmin / hex_width)
        ymin = hex_height * np.floor(ymin / hex_height)
        xmax = hex_width * np.ceil(xmax / hex_width)
        ymax = hex_height * np.ceil(ymax / hex_height)
        return xmin, ymin, xmax, ymax

    @staticmethod
    def tile_positions(xmin, ymin, xmax, ymax, grid_size, side_length):
        """Generate an iterator for all the position where to create a tile."""
        hex_width = 3 * side_length
        cols = np.arange(xmin - hex_width, xmax + hex_width, hex_width)
        rows = np.arange(
            ymin / SIN_60 - side_length, ymax / SIN_60 + side_length, side_length
        )
        return itertools.product(cols, enumerate(rows))

    @staticmethod
    def create_tile_polygon(x, y, grid_size, side_length, i):
        """Create a single hexagon and round geometries to optimize storage."""
        offset = 1.5 * side_length if i % 2 != 0 else 0
        x0 = x - offset
        dim = [
            (x0, y * SIN_60),
            (x0 + side_length, y * SIN_60),
            (x0 + (1.5 * side_length), (y + side_length) * SIN_60),
            (x0 + side_length, (y + (2 * side_length)) * SIN_60),
            (x0, (y + (2 * side_length)) * SIN_60),
            (x0 - (0.5 * side_length), (y + side_length) * SIN_60),
            (x0, y * SIN_60),
        ]
        return Polygon([(round(x, 2), round(y, 2)) for (x, y) in dim], srid=TARGET_PROJ)


def create_tiles_for_city(
    city: DataSource,
    grid_size: float,
    tile_shape_cls: Type[TileShape],
    logger: logging.Logger,
    batch_size: int = int(1e6),
    side_length: Optional[float] = None,
    height_ratio: float = 1,
) -> None:
    """
    Create tiles (square or hexagonal) for a specific city.

    Args:
        city (GeoPandas DataFrame): City GeoDataFrame.
        grid_size (float): The size of the grid in meters.
        tile_shape_cls (class): Class to generate individual tile shapes.
        logger (logging.Logger): The logger object.
        batch_size (int): The size of the batch to save to DB.
        side_length (float, optional): Size of equilateral triangles forming the hexagon.
        height_ratio (float) : The height ratio of the grid element (1 for square and sin(60) for hexs).

    Returns:
        None
    """
    city_geom = city.geometry
    city_geom = city_geom.buffer(20)  # Margin for intersection
    city_id = city.id
    xmin, ymin, xmax, ymax = city_geom.bounds
    # Bounds for the generation
    xmin, ymin, xmax, ymax = tile_shape_cls.adjust_bounds(
        xmin, ymin, xmax, ymax, grid_size, side_length
    )

    tiles = []
    tile_count = 0

    previous_iris = None

    for x, (i, y) in tqdm(
        tile_shape_cls.tile_positions(xmin, ymin, xmax, ymax, grid_size, side_length)
    ):
        tile = box(x, y * height_ratio, x - grid_size, y * height_ratio + grid_size)

        is_intersecting = city_geom.intersects(tile)
        if not is_intersecting:
            continue

        tile_count += 1
        polygon = tile_shape_cls.create_tile_polygon(x, y, grid_size, side_length, i)
        if previous_iris is not None and previous_iris.geometry.intersects(polygon):
            iris_id = previous_iris.id
        else:
            qs = Iris.objects.filter(geometry__intersects=polygon)
            if qs:
                previous_iris = qs[0]
                iris_id = previous_iris.id
            else:
                iris_id = None

        transformed = []
        for c in polygon.coords[0]:
            transformed.append(TRANSFORMATION.transform(*c))

        tile = Tile(
            geometry=polygon,
            map_geometry=Polygon(transformed, srid=TARGET_MAP_PROJ),
            plantability_indice=None,
            plantability_normalized_indice=None,
            city_id=city_id,
            iris_id=iris_id,
        )
        tiles.append(tile)

        # Avoid OOM errors
        if tile_count % batch_size == 0:
            with transaction.atomic():
                Tile.objects.bulk_create(tiles, batch_size=batch_size)
            logger.info(f"Got {len(tiles)} tiles")
            tiles.clear()
            gc.collect()

    if tiles:  # Save last batch
        Tile.objects.bulk_create(tiles, batch_size=batch_size)
    City.objects.filter(id=city.id).update(tiles_generated=True)
