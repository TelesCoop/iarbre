from django.test import TestCase
from iarbre_data.data_config import DATA_FILES, URL_FILES
from iarbre_data.models import Data
from iarbre_data.utils.data_processing import apply_actions
from iarbre_data.management.commands.c03_import_data import (
    download_from_url,
    read_data,
    process_data,
    save_geometries,
)
from iarbre_data.settings import TARGET_PROJ
import geopandas as gpd


class C03DataTestCase(TestCase):
    def setUp(self):
        for idx, dic in enumerate(DATA_FILES):
            if dic["name"] == "Espaces publics":
                idc = idx
                break

        self.data_config = DATA_FILES[idc]
        self.data_config["actions"] = [
            {
                "filters": [
                    {
                        "name": "typeespacepublic",
                        "value": "Parking",
                    },
                    {
                        "name": "typeespacepublic",
                        "value": "Espace piétonnier",
                    },
                ]
            }
        ]
        self.df = read_data(self.data_config)
        self.datas = process_data(self.df, self.data_config)

    def test_download_from_url(self):
        for idx, dic in enumerate(URL_FILES):
            if dic["name"] == "Plan eau":
                idc = idx
                break
        data_config = URL_FILES[idc]
        df_url = download_from_url(data_config["url"], data_config["layer_name"])
        self.assertTrue(isinstance(df_url, gpd.GeoDataFrame))
        self.assertTrue(hasattr(df_url, "geometry"))
        self.assertTrue(df_url.geometry.dtype == "geometry")

    def test_read_data(self):
        self.assertTrue(isinstance(self.df, gpd.GeoDataFrame))
        self.assertTrue(hasattr(self.df, "geometry"))
        self.assertTrue(self.df.geometry.dtype == "geometry")
        self.assertTrue(self.df.geometry.crs == TARGET_PROJ)
        valid_geometries = self.df.geometry.notnull() & self.df.geometry.is_valid
        self.assertTrue(valid_geometries.all())

    def test_apply_actions(self):
        actions = {"buffer_size": 1, "explode": True, "union": True, "simplify": 3}
        df = self.df.copy()[:5]
        df = apply_actions(df, actions)
        self.assertTrue((df.geom_type == "Polygon").all())

        actions = {
            "filters": [
                {
                    "name": "typeespacepublic",
                    "value": "Aire de jeux",
                },
                {
                    "name": "typeespacepublic",
                    "value": "Espace piétonnier",
                },
            ]
        }

        df = apply_actions(self.df, actions)
        self.assertTrue((df.geom_type == "Polygon").all())
        # Empty actions
        df = apply_actions(self.df, {})
        self.assertTrue((df.geom_type == "Polygon").all())

    def test_process_data(self):
        self.assertTrue(isinstance(self.datas, list))

    def test_save_geometries(self):
        save_geometries(self.datas, self.data_config)
        self.assertNotEquals(Data.objects.count(), 0)
