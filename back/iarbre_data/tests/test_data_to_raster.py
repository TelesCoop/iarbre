import os

import numpy as np
import rasterio
import shapely
from django.contrib.gis.geos import Polygon, GEOSGeometry
from django.test import TestCase
from rasterio.transform import from_origin

from iarbre_data.factories import CityFactory
from iarbre_data.management.commands.data_to_raster import (
    rasterize_data_across_all_cities,
)
from iarbre_data.models import Data
import geopandas as gpd


class DataToRasterTestCase(TestCase):
    def setUp(self):
        self.test_output_dir = "test_raster_outputs"
        os.makedirs(self.test_output_dir, exist_ok=True)

        self.cities = [CityFactory() for _ in range(3)]

        city_geoms = [city.geometry for city in self.cities]
        union_geom = city_geoms[0]
        for geom in city_geoms[1:]:
            union_geom = union_geom.union(geom)
        self.all_cities_union = gpd.GeoDataFrame({"geometry": [union_geom]})
        self.all_cities_union.geometry = self.all_cities_union["geometry"].apply(
            lambda el: shapely.wkt.loads(el.wkt)
        )
        self.all_cities_union.set_geometry("geometry")

        minx, miny, maxx, maxy = self.all_cities_union.total_bounds
        resolution = 1
        self.grid_size = 5
        self.width = int((maxx - minx) / resolution)
        self.height = int((maxy - miny) / resolution)
        self.transform = from_origin(minx, maxy, resolution, resolution)

        self.width_out = int((maxx - minx) / self.grid_size)
        self.height_out = int((maxy - miny) / self.grid_size)
        self.transform_out = from_origin(minx, maxy, self.grid_size, self.grid_size)
        # Setup the transform matrices
        self.transform = rasterio.Affine(1.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        self.transform_out = rasterio.Affine(5.0, 0.0, 0.0, 0.0, 5.0, 0.0)

        self.factor_name = "Parking"

        for city in self.cities:
            bbox = city.geometry.extent
            x_min, y_min, x_max, y_max = bbox
            x_center = (x_min + x_max) / 2
            y_center = (y_min + y_max) / 2
            # Create a smaller polygon at the center of the city
            buffer_size = min((x_max - x_min), (y_max - y_min)) * 10
            poly = Polygon.from_bbox(
                (
                    x_center - buffer_size,
                    y_center - buffer_size,
                    x_center + buffer_size,
                    y_center + buffer_size,
                )
            )

            Data.objects.create(factor=self.factor_name, geometry=poly)

    def test_rasterize_data_across_all_cities(self):
        try:
            rasterize_data_across_all_cities(
                factor_name=self.factor_name,
                height=self.height,
                width=self.width,
                height_out=self.height_out,
                width_out=self.width_out,
                transform=self.transform,
                transform_out=self.transform_out,
                all_cities_union=GEOSGeometry(
                    self.all_cities_union.geometry.iloc[0].wkt
                ),
                grid_size=self.grid_size,
                output_dir=self.test_output_dir,
            )

            output_path = os.path.join(self.test_output_dir, f"{self.factor_name}.tif")
            self.assertTrue(os.path.exists(output_path))

            with rasterio.open(output_path, "r") as src:
                output_raster = src.read(1)

                self.assertTrue(np.any(output_raster > 0))
                self.assertEqual(output_raster.shape, (self.height_out, self.width_out))

                self.assertEqual(src.crs.to_string(), "EPSG:2154")
                self.assertEqual(src.transform, self.transform_out)
        finally:
            if os.path.exists(self.test_output_dir):
                import shutil

                shutil.rmtree(self.test_output_dir)
