import os

import mercantile
import mapbox_vector_tile
from iarbre_data.factories import TileFactory
from iarbre_data.models import Tile, MVTTile
from django.test import TestCase
from django.http import HttpRequest
from api.utils.mvt_generator import MVTGenerator, MVTGeneratorWorker
from django.contrib.gis.geos import Polygon
from django.urls import reverse

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
    def tearDown(self):
        # reset_db does not trigger media delete signal
        MVTTile.objects.all().delete()
        return super().tearDown()

    def test_queryset_bounds(self):
        expected_bounds = {
            "west": 4.862904542088828,
            "south": 45.814411026142736,
            "east": 4.908787723340132,
            "north": 45.85159245978295,
        }
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

        mvt_generator = MVTGenerator(Tile, zoom_levels=(8, 10))
        actual_bounds = mvt_generator._get_queryset_bounds()

        # Define a delta for floating-point comparison
        delta = 1e-10

        # Check each value with tolerance
        self.assertAlmostEqual(
            actual_bounds["west"], expected_bounds["west"], delta=delta
        )
        self.assertAlmostEqual(
            actual_bounds["south"], expected_bounds["south"], delta=delta
        )
        self.assertAlmostEqual(
            actual_bounds["east"], expected_bounds["east"], delta=delta
        )
        self.assertAlmostEqual(
            actual_bounds["north"], expected_bounds["north"], delta=delta
        )

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
            Tile,
            zoom_levels=(8, 8),
        )
        mvt_worker = MVTGeneratorWorker(
            Tile.objects.all(),
            geolevel="fake_geolevel",
            datatype="fake_datatype",
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
                mvt_worker._generate_tile_for_zoom(tile, zoom)

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
        mvt = MVTGenerator(
            Tile,
            zoom_levels=(8, 8),
        )
        mvt_worker = MVTGeneratorWorker(
            Tile.objects.all(),
            geolevel="fake_geolevel",
            datatype="fake_datatype",
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
                mvt_worker._generate_tile_for_zoom(tile, zoom)

        qs = MVTTile.objects.all()
        explode_url = qs[0].mvt_file.url.split("/")
        tile_x = int(explode_url[-2])
        tile_y = int(explode_url[-1].split(".")[0])
        tile_zoom = int(explode_url[-3])

        request = HttpRequest()
        request.method = "GET"
        request.META["SERVER_NAME"] = "localhost"
        request.META["SERVER_PORT"] = "8000"

        url = reverse(
            "retrieve-tile",
            args=["fake_geolevel", "fake_datatype", tile_zoom, tile_x, tile_y],
        )
        response = self.client.get(url)

        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(decoded_tile.keys()), ["fake_geolevel--fake_datatype"]
        )
        received_tile = decoded_tile["fake_geolevel--fake_datatype"]["features"][0]
        # https://stackoverflow.com/a/45736752
        self.assertTrue(set(received_tile).issuperset({"geometry", "properties"}))
