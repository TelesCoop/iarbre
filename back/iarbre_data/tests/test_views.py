import os

import mercantile
import mapbox_vector_tile
from iarbre_data.factories import TileFactory
from iarbre_data.models import Tile, MVTTile
from django.test import TestCase
from django.http import HttpRequest
from api.utils.mvt_generator import MVTGenerator
from api.views import tile_view
from django.contrib.gis.geos import Polygon
from django.contrib.gis.db.models.functions import Intersection

from iarbre_data.settings import BASE_DIR

import math


def pixel2deg(xtile, ytile, zoom, xpixel, ypixel, extent=4096):
    """https://gis.stackexchange.com/a/460173"""
    n = 2.0**zoom
    xtile = xtile + (xpixel / extent)
    ytile = ytile + ((extent - ypixel) / extent)
    lon_deg = (xtile / n) * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lon_deg, lat_deg)


class MVTGeneratorTestCase(TestCase):
    def test_queryset_bounds(self):
        poly1 = Polygon.from_bbox(
            [844737.86651438, 6525626.23803353, 846991.45060761, 6528047.95246801]
        )
        poly1.srid = 2154
        TileFactory.create(geometry=poly1)
        poly2 = Polygon.from_bbox(
            [844613.06777516, 6527071.52195335, 848112.69915193, 6529699.83431857]
        )
        poly2.srid = 2154
        TileFactory.create(geometry=poly2)

        qs = Tile.objects.all()
        mvt_generator = MVTGenerator(qs, zoom_levels=(8, 10))
        self.assertDictEqual(
            mvt_generator._get_queryset_bounds(),
            {
                "west": 4.862904542088828,
                "south": 45.814411026142736,
                "east": 4.908787723340132,
                "north": 45.85159245978295,
            },
        )

    def test_transform_to_tile_relative(self):
        mapbox_tile = Polygon.from_bbox(
            [844737.86651438, 6525626.23803353, 846991.45060761, 6528047.95246801]
        )
        mapbox_tile.srid = 2154
        (x0, y0, x_max, y_max) = mapbox_tile.extent
        x_span = x_max - x0
        y_span = y_max - y0

        tilein = Polygon.from_bbox(
            [844737.86651438, 6525626.23803353, 844742.86651438, 6525631.23803353]
        )
        tilein.srid = 2154
        TileFactory.create(geometry=tilein)
        qs = Tile.objects.annotate(
            clipped_geometry=Intersection("map_geometry", mapbox_tile)
        ).first()
        self.assertListEqual(
            [
                (-551198, -1310610),
                (-551198, -1310622),
                (-551211, -1310622),
                (-551211, -1310610),
                (-551198, -1310610),
            ],
            MVTGenerator.transform_to_tile_relative(
                qs.clipped_geometry, x0, y0, x_span, y_span
            ),
        )

    def test_prepare_mvt_features(self):
        mapbox_tile = Polygon.from_bbox(
            [844737.86651438, 6525626.23803353, 846991.45060761, 6528047.95246801]
        )
        mapbox_tile.srid = 2154
        tilein = Polygon.from_bbox(
            [844737.86651438, 6525626.23803353, 844742.86651438, 6525631.23803353]
        )
        tilein.srid = 2154
        TileFactory.create(geometry=tilein)
        qs = Tile.objects.all().annotate(
            clipped_geometry=Intersection("map_geometry", mapbox_tile)
        )
        features = MVTGenerator._prepare_mvt_features(qs, mapbox_tile)
        self.assertEqual(len(features), 1)
        self.assertListEqual(list(features[0].keys()), ["geometry", "properties"])

    def test_generate_tile_for_zoom(self):
        tile1 = Polygon.from_bbox(
            [844737.86651438, 6525626.23803353, 844742.86651438, 6525631.23803353]
        )
        tile1.srid = 2154
        TileFactory.create(geometry=tile1)
        tile2 = Polygon.from_bbox(
            [846992.45060761, 6528048.95246801, 846997.45060761, 6528053.95246801]
        )
        tile2.srid = 2154
        TileFactory.create(geometry=tile2)

        mvt = MVTGenerator(
            Tile.objects.all(), zoom_levels=(8, 8), layer_name="fake_data"
        )
        bounds = mvt._get_queryset_bounds()
        for zoom in range(mvt.min_zoom, mvt.max_zoom + 1):
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
                mvt._generate_tile_for_zoom(tile, zoom)

        qs = MVTTile.objects.all()
        self.assertEqual(len(qs), 1)
        path = str(BASE_DIR) + qs[0].mvt_file.url
        explode_url = qs[0].mvt_file.url.split("/")
        tile_x = int(explode_url[-2])
        tile_y = int(explode_url[-1].split(".")[0])
        tile_zoom = int(explode_url[-3])
        self.assertTrue(os.path.exists(path))

        try:
            with open(path, "rb") as f:
                _ = mapbox_vector_tile.decode(
                    f.read(),
                    transformer=lambda x, y: pixel2deg(tile_x, tile_y, tile_zoom, x, y),
                )
        except Exception:
            raise AssertionError("Can't decode. It's not a mapbox vector tile.")

        # Clean media files before the reset_db does not trigger media delete signal
        MVTTile.objects.all().delete()

    def test_view(self):
        tile1 = Polygon.from_bbox(
            [844737.86651438, 6525626.23803353, 844742.86651438, 6525631.23803353]
        )
        tile1.srid = 2154
        TileFactory.create(geometry=tile1)
        tile2 = Polygon.from_bbox(
            [846992.45060761, 6528048.95246801, 846997.45060761, 6528053.95246801]
        )
        tile2.srid = 2154
        TileFactory.create(geometry=tile2)
        mvt = MVTGenerator(Tile.objects.all(), zoom_levels=(8, 8), layer_name="tile")
        bounds = mvt._get_queryset_bounds()
        for zoom in range(mvt.min_zoom, mvt.max_zoom + 1):
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
                mvt._generate_tile_for_zoom(tile, zoom)

        qs = MVTTile.objects.all()
        explode_url = qs[0].mvt_file.url.split("/")
        tile_x = int(explode_url[-2])
        tile_y = int(explode_url[-1].split(".")[0])
        tile_zoom = int(explode_url[-3])

        request = HttpRequest()
        request.method = "GET"
        request.META["SERVER_NAME"] = "localhost"
        request.META["SERVER_PORT"] = "8000"
        response = tile_view(
            request=request, model_type="tile", zoom=tile_zoom, x=tile_x, y=tile_y
        )
        decoded_tile = mapbox_vector_tile.decode(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertListEqual(list(decoded_tile.keys()), ["tile"])
        received_tile = decoded_tile["tile"]["features"][0]
        # https://stackoverflow.com/a/45736752
        self.assertTrue(set(received_tile).issuperset({"geometry", "properties"}))

        # Clean media files before the reset_db does not trigger media delete signal
        MVTTile.objects.all().delete()
