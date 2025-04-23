import os
import tempfile
import numpy as np
import rasterio
from django.test import TestCase

from plantability.management.commands.compute_plantability_raster import (
    compute_weighted_sum,
    threshold_and_convert_to_colors,
)
from plantability.constants import colors, rgb_colors


class ComputePlantabilityRasterTestCase(TestCase):
    def setUp(self):
        """Setup test rasters with geometric shapes"""

        self.temp_dir = tempfile.mkdtemp()
        self.raster_directory = self.temp_dir + "/"

        self.width = 100
        self.height = 100

        self.meta = {
            "driver": "GTiff",
            "height": self.height,
            "width": self.width,
            "count": 1,
            "dtype": rasterio.dtypes.float32,
            "crs": "+proj=utm +zone=10 +datum=WGS84",
            "transform": rasterio.transform.from_origin(0, 0, 1, 1),
        }

        # Create "Parking" raster with 3 rectangles
        parking_data = np.zeros((self.height, self.width), dtype=np.float32)
        parking_data[10:30, 10:40] = 1
        parking_data[40:60, 40:80] = 1
        self.parking_file = os.path.join(self.raster_directory, "Parking.tif")
        with rasterio.open(self.parking_file, "w", **self.meta) as dst:
            dst.write(parking_data, 1)

        # Create "Bâtiments" raster with 5 squares
        buildings_data = np.zeros((self.height, self.width), dtype=np.float32)
        buildings_data[5:25, 5:25] = 1
        buildings_data[30:50, 30:50] = 1
        buildings_data[60:80, 10:30] = 1
        buildings_data[20:40, 60:80] = 1
        buildings_data[70:90, 70:90] = 1

        self.buildings_file = os.path.join(self.raster_directory, "Bâtiments.tif")
        with rasterio.open(self.buildings_file, "w", **self.meta) as dst:
            dst.write(buildings_data, 1)

        self.parking_data = parking_data
        self.buildings_data = buildings_data

        result = np.zeros((self.height, self.width), dtype=np.float32)

        output_file = os.path.join(self.temp_dir, "weighted_sum_output.tif")

        # Arbitrary weigth for tests
        self.FACTORS = {"Parking": +3, "Bâtiments": -5}
        for factor, weight in self.FACTORS.items():
            compute_weighted_sum(
                self.raster_directory,
                output_file,
                self.meta.copy(),
                result,
                factor,
                weight,
            )
        with rasterio.open(output_file) as src:
            self.final_result = src.read(1)

    def test_compute_weighted_sum(self):
        """Test compute_weighted_sum function accurately calculates weighted sum of rasters"""
        try:
            overlap_region = self.final_result[10:25, 10:25]
            expected_overlap = (self.FACTORS["Parking"] / 100) + (
                self.FACTORS["Bâtiments"] / 100
            )
            self.assertEqual(np.mean(overlap_region), expected_overlap)
        finally:
            if os.path.exists(self.temp_dir):
                import shutil

                shutil.rmtree(self.temp_dir)

    def test_threshold_and_convert_to_colors(self):
        result = self.final_result.copy()
        # Include some nodata values for testing
        result[0:5, 0:5] = -9999

        result_colors = threshold_and_convert_to_colors(result, rgb_colors, colors)

        # Test if it is RGB
        expected_shape = result.shape + (3,)
        self.assertEqual(result_colors.shape, expected_shape)

        # Test nodata in white
        self.assertEqual(
            result[0, 0].all(), np.array([255, 255, 255], dtype=np.uint8).all()
        )

        # In parking
        self.assertEqual(
            result[15, 15].all(), np.array(rgb_colors[2.5], dtype=np.uint8).all()
        )

        # In Batiments
        self.assertEqual(
            result[85, 85].all(), np.array(rgb_colors[-5], dtype=np.uint8).all()
        )
