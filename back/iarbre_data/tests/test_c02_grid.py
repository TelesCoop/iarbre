from django.test import TestCase
from iarbre_data.management.commands.c01_insert_cities_and_iris import (
    Command as c01_city_iris,
)
from iarbre_data.management.commands.c02_init_grid import (
    create_tiles_for_city,
    SquareTileShape,
    HexTileShape,
    clean_outside,
)
from iarbre_data.management.commands.utils import select_city, load_geodataframe_from_db
from iarbre_data.settings import BASE_DIR
from iarbre_data.models import Tile, City
from iarbre_data.tests.test_c01_iris_city import move_test_data
import numpy as np
import logging


class C02GridTestCase(TestCase):
    def setUp(self):
        move_test_data()
        data = str(BASE_DIR) + "/file_data/communes_gl_2025.geojson"
        c01_city_iris._insert_cities(data)
        self.grid_size = 200
        desired_area = self.grid_size * self.grid_size
        self.side_length = np.sqrt((2 * desired_area) / (3 * np.sqrt(3)))
        self.sin_60 = np.sin(np.pi / 3)

    def test_create_square_tile(self):
        code = 69286
        selected_city = select_city(str(code))
        print("Creating tiles")
        create_tiles_for_city(
            city=selected_city.iloc[0],
            grid_size=self.grid_size,
            tile_shape_cls=SquareTileShape,
            logger=logging.getLogger(__name__),
            batch_size=int(1e6),
        )
        qs = City.objects.filter(code=code)
        df = load_geodataframe_from_db(qs, ["tiles_generated"])
        self.assertTrue(df.tiles_generated.values)
        self.assertEqual(Tile.objects.count(), 587)
        tile = Tile.objects.first()
        self.assertEqual(tile.geometry.area, self.grid_size**2)
        coords = tile.geometry.coords[0]
        self.assertEqual(len(coords), 5)  # it's a square
        self.assertEqual(coords[0][0] - coords[2][0], self.grid_size)
        self.assertEqual(coords[1][1] - coords[0][1], self.grid_size)

    def test_create_hex_tile(self):
        code = 69286
        selected_city = select_city(str(code))
        create_tiles_for_city(
            city=selected_city.iloc[0],
            grid_size=self.grid_size,
            tile_shape_cls=HexTileShape,
            logger=logging.getLogger(__name__),
            batch_size=int(1e6),
            side_length=self.side_length,
            height_ratio=self.sin_60,
        )
        qs = City.objects.filter(code=code)
        df = load_geodataframe_from_db(qs, ["tiles_generated"])
        self.assertTrue(df.tiles_generated.values)
        self.assertEqual(Tile.objects.count(), 593)
        tile = Tile.objects.first()
        self.assertEqual(int(tile.geometry.area), self.grid_size**2)
        coords = tile.geometry.coords[0]
        self.assertEqual(len(coords), 7)  # it's a hex
        self.assertEqual(int(coords[1][0] - coords[0][0]), int(self.side_length))
        self.assertEqual(
            int(coords[2][1] - coords[0][1]), int(self.sin_60 * self.side_length)
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
                side_length=self.side_length,
                height_ratio=self.sin_60,
            )
        selected_city = select_city(str(codes[0]))
        clean_outside(selected_city, 1e4)
        self.assertFalse(
            City.objects.filter(code=codes[1])[0].geometry.intersects(
                Tile.objects.first().geometry
            )
        )
