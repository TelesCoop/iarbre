import os
import tempfile
import numpy as np
import rasterio
from django.test import TestCase

from plantability.management.commands.compute_plantability_raster import (
    compute_weighted_sum,
    keep_planting_spots,
    remove_isolated_pixels,
    threshold_and_convert_to_colors,
    BLOCKING_SCORE,
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

        # Arbitrary weight for tests; Bâtiments is the blocking factor
        self.FACTORS = {"Parking": +3, "Bâtiments": -5}

        blocked = np.zeros((self.height, self.width), dtype=bool)
        blocked |= buildings_data > 0

        for factor, weight in self.FACTORS.items():
            if weight == BLOCKING_SCORE:
                continue
            compute_weighted_sum(
                self.raster_directory,
                output_file,
                self.meta.copy(),
                result,
                blocked,
                factor,
                weight,
            )
        result[blocked] = BLOCKING_SCORE

        meta_out = self.meta.copy()
        meta_out.update(dtype=np.float32, count=1, compress="lzw", nodata=-9999)
        with rasterio.open(output_file, "w", **meta_out) as dst:
            dst.write(result, 1)

        with rasterio.open(output_file) as src:
            self.final_result = src.read(1)

    def test_compute_weighted_sum(self):
        """Test compute_weighted_sum function accurately calculates weighted sum of rasters"""
        try:
            # Overlap of parking and buildings: blocked pixels must be BLOCKING_SCORE
            overlap_region = self.final_result[10:25, 10:25]
            self.assertTrue(np.all(overlap_region == BLOCKING_SCORE))

            # Pure parking region (row 26:30, col 26:40 — outside buildings bounds)
            pure_parking_region = self.final_result[26:30, 26:40]
            expected_parking = self.FACTORS["Parking"] / 100
            self.assertAlmostEqual(
                float(np.mean(pure_parking_region)), expected_parking
            )

            # Pure buildings region (not overlapping parking): blocked
            pure_buildings_region = self.final_result[70:90, 70:90]
            self.assertTrue(np.all(pure_buildings_region == BLOCKING_SCORE))
        finally:
            if os.path.exists(self.temp_dir):
                import shutil

                shutil.rmtree(self.temp_dir)

    def test_threshold_and_convert_to_colors(self):
        result = self.final_result.copy()
        # Include some nodata values for testing
        result[0:5, 0:5] = -9999

        result_colors = threshold_and_convert_to_colors(result, rgb_colors, colors)

        # Test if it is RGBA
        expected_shape = result.shape + (4,)
        self.assertEqual(result_colors.shape, expected_shape)
        self.assertEqual(result_colors[75, 75, 3], 0)
        self.assertEqual(result_colors[27, 30, 3], 255)
        self.assertEqual(tuple(result_colors[0, 0]), (255, 255, 255, 255))

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

    def test_remove_isolated_pixels(self):
        result = np.full((9, 9), 3.0, dtype=np.float32)
        result[0:3, 0:3] = 1.0
        result[1, 1] = -3.0
        result[5, 5] = 1.0
        result[6, 6] = 1.0
        result[7, 1] = BLOCKING_SCORE
        result[4, 7] = 6.0
        blocked = result == BLOCKING_SCORE

        result = remove_isolated_pixels(result, blocked)

        self.assertAlmostEqual(result[1, 1], 1.0)
        self.assertEqual(result[5, 5], 1.0)
        self.assertEqual(result[6, 6], 1.0)
        self.assertEqual(result[7, 1], BLOCKING_SCORE)
        self.assertEqual(result[4, 4], 3.0)
        self.assertEqual(result[4, 7], 6.0)

    def test_keep_planting_spots(self):
        result = np.zeros((12, 12), dtype=np.float32)
        result[1:5, 1:5] = 3.0
        result[7:12, 1:4] = 3.0
        result[6, 8] = -3.0
        result[9, 9] = BLOCKING_SCORE
        result[9, 10] = -8.0
        blocked = result == BLOCKING_SCORE

        result = keep_planting_spots(result, blocked, 1.0)

        self.assertTrue(np.all(result[1:5, 1:5] == 3.0))
        self.assertEqual(result[0:6, 0:6].sum(), 3.0 * 16)
        self.assertTrue(np.all(result[7:12, 1:4] == 0.0))
        self.assertEqual(result[6, 8], -3.0)
        self.assertEqual(result[9, 9], BLOCKING_SCORE)
