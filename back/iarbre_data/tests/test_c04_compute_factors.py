import logging

from django.test import TestCase

from iarbre_data.management.commands.c02_init_grid import (
    create_tiles_for_city,
    HexTileShape,
)
from iarbre_data.management.commands.c03_import_data import (
    read_data,
    process_data,
    save_geometries,
)
from iarbre_data.management.commands.c04_compute_factors import (
    process_city,
    compute_for_factor,
    _compute_for_factor_partial_tiles,
)
from iarbre_data.management.commands.c01_insert_cities_and_iris import (
    Command as c01_city_iris,
)
import numpy as np

from iarbre_data.management.commands.utils import select_city, load_geodataframe_from_db
from iarbre_data.models import Tile, Data, TileFactor, City
from iarbre_data.settings import BASE_DIR
from iarbre_data.data_config import DATA_FILES
from iarbre_data.tests.test_c01_iris_city import move_test_data


class C04ComputeFactorsTestCase(TestCase):
    def setUp(self):
        move_test_data()
        data = str(BASE_DIR) + "/file_data/communes_gl_2025.geojson"
        c01_city_iris()._insert_cities(data)
        grid_size = 100
        desired_area = grid_size * grid_size
        unit = np.sqrt((2 * desired_area) / (3 * np.sqrt(3)))
        a = np.sin(np.pi / 3)
        self.code = 69381
        selected_city = select_city(str(self.code))
        self.city = selected_city.iloc[0]
        create_tiles_for_city(
            self.city,
            grid_size,
            HexTileShape,
            logger=logging.getLogger(__name__),
            batch_size=int(1e6),
            unit=unit,
            a=a,
        )
        data_config = DATA_FILES[0]
        df = read_data(data_config)
        datas = process_data(df, data_config)
        save_geometries(datas, data_config)
        self.FACTORS = {data_config["factors"][0]: 1}
        self.tiles = load_geodataframe_from_db(Tile.objects.all(), ["id"])
        self.std_area = Tile.objects.first().geometry.area
        self.factor_name = list(self.FACTORS.keys())[0]

    def test__compute_partial_tiles_empty(self):
        qs = Data.objects.filter(factor=self.factor_name)
        factor_df = load_geodataframe_from_db(qs, [])

        res_df = _compute_for_factor_partial_tiles(factor_df, self.tiles, self.std_area)
        res_df_direct = self.tiles.clip(factor_df)
        res_df_direct["value"] = res_df_direct.geometry.area / self.std_area
        try:
            diff = np.mean(np.abs(res_df["value"] - res_df_direct["value"]))
        except Exception:
            raise AssertionError("The factor value computation is not correct.")
        self.assertListEqual(list(res_df.id), list(res_df_direct.id))
        if diff is not np.nan:  # Empty clipping
            self.assertTrue(diff < 1e-5)

    def test_compute_for_factor(self):
        compute_for_factor(self.factor_name, self.tiles, self.std_area)
        self.assertNotEquals(TileFactor.objects.count(), 0)
        self.assertEqual(TileFactor.objects.first().factor, self.factor_name)

    def test_process_city(self):
        self.assertEquals(City.objects.filter(tiles_computed=True).count(), 0)
        process_city(self.city, self.FACTORS, self.std_area, False)
        self.assertNotEquals(City.objects.filter(tiles_computed=True).count(), 0)
        city = City.objects.filter(code=self.code)[0]
        completion = process_city(city, self.FACTORS, self.std_area, False)
        self.assertEqual(completion, 0)
