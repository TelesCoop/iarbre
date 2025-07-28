from django.test import TestCase
from iarbre_data.data_config import DATA_FILES, URL_FILES
from iarbre_data.models import Data
from iarbre_data.utils.data_processing import apply_actions
from iarbre_data.management.commands.c03_import_data import (
    download_from_url,
    download_dbtopo,
    download_cerema,
    read_data,
    process_data,
    save_geometries,
)
from iarbre_data.settings import TARGET_PROJ
import geopandas as gpd


class C03DataTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for idx, dic in enumerate(DATA_FILES):
            if dic["name"] == "Espaces publics":
                idc = idx
                break

        cls.data_config = DATA_FILES[idc]
        cls.data_config["actions"] = [
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
        cls.df = read_data(cls.data_config)
        cls.datas = process_data(cls.df, cls.data_config)

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

    def test_read_data_url_paths(self):
        bd_topo_config = {"url": "https://data.geopf.fr/test", "name": "Test BD TOPO"}
        df = download_dbtopo(bd_topo_config["url"])
        self.assertTrue(isinstance(df, gpd.GeoDataFrame))

        cerema_config = {"url": "https://cerema.test.fr/api", "name": "Test CEREMA"}
        df = download_cerema(cerema_config["url"])
        self.assertTrue(isinstance(df, gpd.GeoDataFrame))

    def test_read_data_with_layer_name(self):
        """Test read_data function with layer_name parameter."""
        # Find a config with layer_name
        config_with_layer = None
        for config in DATA_FILES:
            if config.get("layer_name"):
                config_with_layer = config
                break

        if config_with_layer:
            df = read_data(config_with_layer)
            self.assertTrue(isinstance(df, gpd.GeoDataFrame))
            self.assertEqual(df.crs, TARGET_PROJ)

    def test_read_data_without_layer_name(self):
        """Test read_data function without layer_name parameter."""
        # Find a config without layer_name
        config_without_layer = None
        for config in DATA_FILES:
            if not config.get("layer_name") and not config.get("url"):
                config_without_layer = config
                break

        if config_without_layer:
            df = read_data(config_without_layer)
            self.assertTrue(isinstance(df, gpd.GeoDataFrame))
            self.assertEqual(df.crs, TARGET_PROJ)

    def test_read_data_geometry_validation(self):
        df = read_data(self.data_config)
        # All geometries should be valid and non-null
        self.assertTrue(df.geometry.notnull().all())
        self.assertTrue(df.geometry.is_valid.all())
        # Geometries should be 2D
        self.assertTrue(
            all(geom.has_z is False for geom in df.geometry if geom is not None)
        )

    def test_crs_conversion(self):
        df = read_data(self.data_config)
        self.assertEqual(df.crs, TARGET_PROJ)

    def test_process_data_returns_list(self):
        result = process_data(self.df, self.data_config)
        self.assertIsInstance(result, list)
        if result:  # If list is not empty
            # Each item should be a data object that can be saved
            self.assertIsInstance(result[0], dict)

    def test_save_geometries_with_existing_data(self):
        # Save data first time
        save_geometries(self.datas, self.data_config)
        Data.objects.filter(metadata=self.data_config["name"]).count()

        # Save same data again
        save_geometries(self.datas, self.data_config)
        final_count = Data.objects.filter(metadata=self.data_config["name"]).count()

        # Should have data (either kept or replaced)
        self.assertGreater(final_count, 0)
