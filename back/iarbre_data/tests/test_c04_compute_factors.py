import logging

from django.test import TestCase

from iarbre_data.management.commands.c02_init_grid import create_tiles_for_city, HexTileShape
from iarbre_data.management.commands.c03_import_data import read_data, process_data, save_geometries
from iarbre_data.management.commands.c04_compute_factors import
from iarbre_data.management.commands.c01_insert_cities_and_iris import (
    Command as c01_city_iris,
)
import numpy as np

from iarbre_data.management.commands.utils import select_city
from iarbre_data.settings import BASE_DIR
from iarbre_data.data_config import FACTORS, DATA_FILES


class c04_computefactorsTestCase(TestCase):
    def setUp(self):
        data = str(BASE_DIR) + "/file_data/communes_gl_2025.geojson"
        c01_city_iris()._insert_cities(data)
        grid_size = 200
        desired_area = grid_size * grid_size
        unit = np.sqrt((2 * desired_area) / (3 * np.sqrt(3)))
        a = np.sin(np.pi / 3)
        code = 69381
        selected_city = select_city(str(code))
        create_tiles_for_city(
            selected_city.iloc[0],
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

