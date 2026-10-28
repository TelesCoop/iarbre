import os
import shutil

import numpy as np
import rasterio
import shapely
from django.contrib.gis.geos import Polygon, GEOSGeometry
from django.core.management import call_command
from django.test import TestCase
from rasterio.transform import from_origin

from iarbre_data.data_config import FACTORS
from iarbre_data.settings import SRID_DB
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
        self.addCleanup(shutil.rmtree, self.test_output_dir, ignore_errors=True)

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
        rasterize_data_across_all_cities(
            factor_name=self.factor_name,
            height=self.height,
            width=self.width,
            height_out=self.height_out,
            width_out=self.width_out,
            transform=self.transform,
            transform_out=self.transform_out,
            all_cities_union=GEOSGeometry(self.all_cities_union.geometry.iloc[0].wkt),
            grid_size=self.grid_size,
            output_dir=self.test_output_dir,
        )

        output_path = os.path.join(self.test_output_dir, f"{self.factor_name}.tif")
        self.assertTrue(os.path.exists(output_path))

        with rasterio.open(output_path, "r") as src:
            output_raster = src.read(1)

            self.assertTrue(np.any(output_raster > 0))
            self.assertEqual(output_raster.shape, (self.height_out, self.width_out))

            self.assertEqual(src.crs.to_string(), f"EPSG:{SRID_DB}")
            self.assertEqual(src.transform, self.transform_out)

    def test_rasterize_blank_factor(self):
        kwargs = dict(
            factor_name="Absent",
            height=self.height,
            width=self.width,
            height_out=self.height_out,
            width_out=self.width_out,
            transform=self.transform,
            transform_out=self.transform_out,
            all_cities_union=GEOSGeometry(self.all_cities_union.geometry.iloc[0].wkt),
            grid_size=self.grid_size,
            output_dir=self.test_output_dir,
        )
        with self.assertRaises(ValueError):
            rasterize_data_across_all_cities(**kwargs)

        rasterize_data_across_all_cities(**kwargs, allow_blank=True)
        output_path = os.path.join(self.test_output_dir, "Absent.tif")
        with rasterio.open(output_path, "r") as src:
            output_raster = src.read(1)
            self.assertFalse(np.any(output_raster))
            self.assertEqual(output_raster.shape, (self.height_out, self.width_out))
            self.assertEqual(src.transform, self.transform_out)

    def test_rasterize_with_exclude(self):
        city_geometry = self.cities[0].geometry
        Data.objects.create(factor="Hole", geometry=city_geometry)
        minx, _, _, maxy = self.all_cities_union.total_bounds
        kwargs = dict(
            factor_name=self.factor_name,
            height=self.height,
            width=self.width,
            height_out=self.height_out,
            width_out=self.width_out,
            transform=from_origin(minx, maxy, 1, 1),
            transform_out=from_origin(minx, maxy, self.grid_size, self.grid_size),
            all_cities_union=GEOSGeometry(self.all_cities_union.geometry.iloc[0].wkt),
            grid_size=self.grid_size,
            output_dir=self.test_output_dir,
            allow_blank=True,
        )
        output_path = os.path.join(self.test_output_dir, f"{self.factor_name}.tif")
        rasterize_data_across_all_cities(**kwargs)
        with rasterio.open(output_path, "r") as src:
            full = src.read(1).astype(int).sum()
        rasterize_data_across_all_cities(**kwargs, exclude=[("data", "Hole")])
        with rasterio.open(output_path, "r") as src:
            holed = src.read(1).astype(int).sum()
        self.assertLess(holed, full)

    def test_command_bbox(self):
        minx, miny, maxx, maxy = self.cities[0].geometry.extent
        bbox = [minx, miny, minx + 100, miny + 50]
        for grid_size in (1, 5):
            with self.subTest(grid_size=grid_size):
                call_command(
                    "data_to_raster",
                    "--grid-size",
                    str(grid_size),
                    "--bbox",
                    *[str(v) for v in bbox],
                    "--output-dir",
                    self.test_output_dir,
                )
                for factor_name in FACTORS:
                    if factor_name == "QPV":
                        continue
                    output_path = os.path.join(
                        self.test_output_dir, f"{factor_name}.tif"
                    )
                    with rasterio.open(output_path, "r") as src:
                        self.assertEqual(src.shape, (50 // grid_size, 100 // grid_size))
                        self.assertEqual(
                            src.transform,
                            from_origin(minx, miny + 50, grid_size, grid_size),
                        )

    def test_rasterize_fine_grid(self):
        minx, _, _, maxy = self.all_cities_union.total_bounds
        rasterize_data_across_all_cities(
            factor_name=self.factor_name,
            height=self.height,
            width=self.width,
            height_out=self.height,
            width_out=self.width,
            transform=from_origin(minx, maxy, 1, 1),
            transform_out=from_origin(minx, maxy, 1, 1),
            all_cities_union=GEOSGeometry(self.all_cities_union.geometry.iloc[0].wkt),
            grid_size=1,
            output_dir=self.test_output_dir,
        )
        output_path = os.path.join(self.test_output_dir, f"{self.factor_name}.tif")
        with rasterio.open(output_path, "r") as src:
            self.assertEqual(set(np.unique(src.read(1))), {100})

    def test_tile_aggregates_its_own_pixels(self):
        minx, _, _, maxy = self.all_cities_union.total_bounds
        centroid = self.cities[0].geometry.centroid
        col = int((centroid.x - minx) // self.grid_size)
        row = int((maxy - centroid.y) // self.grid_size)
        tile = Polygon.from_bbox(
            (
                minx + col * self.grid_size,
                maxy - (row + 1) * self.grid_size,
                minx + (col + 1) * self.grid_size,
                maxy - row * self.grid_size,
            )
        )
        tile.srid = SRID_DB
        Data.objects.create(factor="Tile", geometry=tile)
        rasterize_data_across_all_cities(
            factor_name="Tile",
            height=self.height,
            width=self.width,
            height_out=self.height_out,
            width_out=self.width_out,
            transform=from_origin(minx, maxy, 1, 1),
            transform_out=from_origin(minx, maxy, self.grid_size, self.grid_size),
            all_cities_union=GEOSGeometry(self.all_cities_union.geometry.iloc[0].wkt),
            grid_size=self.grid_size,
            output_dir=self.test_output_dir,
        )
        with rasterio.open(os.path.join(self.test_output_dir, "Tile.tif")) as src:
            output_raster = src.read(1)
        self.assertEqual(output_raster[row, col], 100)
        self.assertEqual(output_raster.sum(), 100)
