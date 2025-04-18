from django.test import TestCase
from shapely.geometry.polygon import Polygon

from iarbre_data.management.commands.c01_insert_cities_and_iris import (
    Command as c01_city_iris,
)
from iarbre_data.management.commands.c02_init_grid import (
    create_tiles_for_city,
    SquareTileShape,
    HexTileShape,
    clean_outside,
)
from iarbre_data.utils.database import select_city, load_geodataframe_from_db
from iarbre_data.settings import BASE_DIR
from iarbre_data.models import Tile, City
import numpy as np
import logging


class C02GridTestCase(TestCase):
    def setUp(self):
        data = str(BASE_DIR) + "/file_data/communes_gl_2025.geojson"
        c01_city_iris._insert_cities(data)
        # Lyon-Part Dieu
        x, y = 844612.097181, 6519563.100231
        side = 400  # meters
        half_side = side / 2
        # square with center on Lyon Part-Dieu and side 400m
        city_geometry = Polygon(
            [
                (x - half_side, y - half_side),
                (x + half_side, y - half_side),
                (x + half_side, y + half_side),
                (x - half_side, y + half_side),
                (x - half_side, y - half_side),
            ]
        )
        city = City(
            name="square-city",
            code="69000",
            tiles_generated=False,
            tiles_computed=False,
            geometry=city_geometry.wkt,
        )
        city.save()

        self.grid_size = 200  # meters

        # This is the hexagonal side length in order to have
        # an hex with a surface area of 200x200 m^2
        tile_area = self.grid_size * self.grid_size
        self.hex_side_length = np.sqrt((2 * tile_area) / (3 * np.sqrt(3)))
        self.sin_60 = np.sin(np.pi / 3)

    @staticmethod
    def check_overlapping_tiles(tiles):
        tiles = list(Tile.objects.all())
        overlapping_tiles = []
        for tile in tiles:
            if (
                Tile.objects.filter(geometry__overlaps=tile.geometry)
                .exclude(id=tile.id)
                .exists()
            ):
                overlapping_tiles.append(tile.id)
        return overlapping_tiles

    @staticmethod
    def tile_covert_city(city, tiles):
        covert_city = False
        city_area = city.geometry.area
        tile_area = sum(tile.geometry.area for tile in tiles)
        if tile_area > city_area:
            covert_city = True
        return covert_city

    def test_create_square_tile(self):
        selected_city = select_city("69000")

        print("Creating tiles")
        create_tiles_for_city(
            city=selected_city.iloc[0],
            grid_size=self.grid_size,
            tile_shape_cls=SquareTileShape,
            logger=logging.getLogger(__name__),
            batch_size=int(1e6),
        )
        qs = City.objects.filter(name="square-city")
        df = load_geodataframe_from_db(qs, ["tiles_generated"])

        self.assertTrue(df.tiles_generated.values)

        tiles = list(Tile.objects.all())
        overlapping_tiles = self.check_overlapping_tiles(tiles)
        self.assertFalse(overlapping_tiles)

        city = City.objects.get(name="square-city")
        covert_city = self.tile_covert_city(city, tiles)
        self.assertTrue(covert_city)

        tile = Tile.objects.first()
        self.assertEqual(tile.geometry.area, self.grid_size**2)
        coords = tile.geometry.coords[0]
        self.assertEqual(len(coords), 5)  # it's a square
        self.assertEqual(coords[0][0] - coords[2][0], self.grid_size)
        self.assertEqual(coords[1][1] - coords[0][1], self.grid_size)

    def test_create_hex_tile(self):
        selected_city = select_city("69000")
        create_tiles_for_city(
            city=selected_city.iloc[0],
            grid_size=self.grid_size,
            tile_shape_cls=HexTileShape,
            logger=logging.getLogger(__name__),
            batch_size=int(1e6),
            side_length=self.hex_side_length,
            height_ratio=self.sin_60,
        )
        qs = City.objects.filter(name="square-city")
        df = load_geodataframe_from_db(qs, ["tiles_generated"])
        self.assertTrue(df.tiles_generated.values)

        tiles = list(Tile.objects.all())
        overlapping_tiles = self.check_overlapping_tiles(tiles)
        self.assertFalse(overlapping_tiles)

        city = City.objects.get(name="square-city")
        covert_city = self.tile_covert_city(city, tiles)
        self.assertTrue(covert_city)

        tile = Tile.objects.first()
        self.assertEqual(int(tile.geometry.area), self.grid_size**2)
        coords = tile.geometry.coords[0]
        self.assertEqual(len(coords), 7)  # it's a hex
        self.assertEqual(int(coords[1][0] - coords[0][0]), int(self.hex_side_length))
        self.assertEqual(
            int(coords[2][1] - coords[0][1]), int(self.sin_60 * self.hex_side_length)
        )

    def test_clean_outside(self):
        codes = [69286, 69071]
        for code in codes:
            selected_city = select_city(str(code))
            create_tiles_for_city(
                selected_city.iloc[0],
                self.grid_size,
                HexTileShape,
                logger=logging.getLogger(__name__),
                batch_size=int(1e6),
                side_length=self.hex_side_length,
                height_ratio=self.sin_60,
            )
        selected_city = select_city(str(codes[0]))
        clean_outside(selected_city, int(1e4))
        self.assertFalse(
            City.objects.filter(code=codes[1])[0].geometry.intersects(
                Tile.objects.first().geometry
            )
        )
