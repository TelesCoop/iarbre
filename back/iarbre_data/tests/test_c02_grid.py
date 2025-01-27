from django.test import TestCase
from iarbre_data.management.commands.c01_insert_cities_and_iris import Command as c01_city_iris
from iarbre_data.management.commands.c02_init_grid import create_tiles_for_city, SquareTileShape, HexTileShape, clean_outside
from iarbre_data.management.commands.utils import select_city, load_geodataframe_from_db
from iarbre_data.settings import BASE_DIR
from iarbre_data.models import Tile, City
import numpy as np
import logging

class c02_gridTestCase(TestCase):
    def setUp(self):
        data = str(BASE_DIR) + "/file_data/communes_gl_2025.geojson"
        c01_city_iris._insert_cities(data)
        self.grid_size = 200
        desired_area = self.grid_size * self.grid_size
        self.unit = np.sqrt((2 * desired_area) / (3 * np.sqrt(3)))
        self.a = np.sin(np.pi / 3)

    def test_create_square_tile(self):
        code = 69381
        selected_city = select_city(str(code))

        create_tiles_for_city(
            selected_city.iloc[0],
            self.grid_size,
            SquareTileShape,
            logger = logging.getLogger(__name__),
            batch_size=int(1e6),
            a=None
        )
        qs = City.objects.filter(code=code)
        df = load_geodataframe_from_db(qs, ["tiles_generated"])
        self.assertTrue(df.tiles_generated.values)
        self.assertEqual(Tile.objects.count(), 37)
        tile = Tile.objects.first()
        self.assertEqual(tile.geometry.area, self.grid_size**2)
        coords = tile.geometry.coords[0]
        self.assertEqual(len(coords), 5) # it's a square
        self.assertEqual(coords[0][0] - coords[2][0], self.grid_size)
        self.assertEqual(coords[1][1] - coords[0][1], self.grid_size)
        self.assertTrue(City.objects.filter(code=code)[0].geometry.intersects(tile.geometry))

    def test_create_hex_tile(self):
        code = 69381
        selected_city = select_city(str(code))

        create_tiles_for_city(
            selected_city.iloc[0],
            self.grid_size,
            HexTileShape,
            logger = logging.getLogger(__name__),
            batch_size=int(1e6),
            unit=self.unit,
            a=self.a
        )
        qs = City.objects.filter(code=code)
        df = load_geodataframe_from_db(qs, ["tiles_generated"])
        self.assertTrue(df.tiles_generated.values)
        self.assertEqual(Tile.objects.count(), 36)
        tile = Tile.objects.first()
        self.assertEqual(int(tile.geometry.area), self.grid_size**2 - 1)
        coords = tile.geometry.coords[0]
        self.assertEqual(len(coords), 7) # it's a hex
        self.assertEqual(int(coords[1][0] - coords[0][0]), int(self.unit))
        self.assertEqual(int(coords[2][1] - coords[0][1]), int(self.a*self.unit))
        self.assertTrue(City.objects.filter(code=code)[0].geometry.intersects(tile.geometry))


    def test_clean_outside(self):
        codes = [69381, 69382]
        for code in codes:
            selected_city = select_city(str(code))
            create_tiles_for_city(
                selected_city.iloc[0],
                self.grid_size,
                HexTileShape,
                logger=logging.getLogger(__name__),
                batch_size=int(1e6),
                unit=self.unit,
                a=self.a
            )
        selected_city = select_city(str(codes[0]))
        clean_outside(selected_city, 1e4)
        self.assertFalse(City.objects.filter(code=codes[1])[0].geometry.intersects(Tile.objects.first().geometry))


