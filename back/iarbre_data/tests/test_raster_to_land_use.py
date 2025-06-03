import os
import json
import numpy as np
import rasterio
import tempfile
from django.test import TestCase
from django.contrib.gis.geos import Polygon
from rasterio.transform import from_origin

from iarbre_data.models import Tile
from iarbre_data.management.commands.raster_to_land_use import process_tile_batch


class RasterToLandUse(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.raster_path = self.temp_dir.name
        self.raster_files = ["Parking.tif", "Bâtiments.tif", "Giratoires.tif"]
        self.create_test_rasters()
        ids = self.create_test_tiles()
        self.tiles = Tile.objects.filter(id__in=ids)

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_test_rasters(self):
        """Create test raster files with synthetic data for testing."""

        height, width = 100, 100
        transform = from_origin(0, 100, 1, 1)

        # Define the raster metadata
        meta = {
            "driver": "GTiff",
            "height": height,
            "width": width,
            "count": 1,
            "dtype": rasterio.float32,
            "crs": "EPSG:2154",
            "transform": transform,
        }

        for i, land_type in enumerate(self.raster_files):
            data = np.zeros((height, width), dtype=np.float32)
            land_type = land_type.split(".")[0]
            # Set specific areas with different values
            if land_type == "Parking":
                # Parking in the top part
                data[10:40, 20:80] = 80.0
            elif land_type == "Bâtiments":
                # Bâtiment in the middle part
                data[30:70, 30:70] = 60.0
            elif land_type == "Giratoires":
                # Giratoires in the bottom part
                data[60:90, 40:60] = 40.0

            # Save the raster file
            raster_file = os.path.join(self.raster_path, f"{land_type}.tif")
            with rasterio.open(raster_file, "w", **meta) as dst:
                dst.write(data.astype(rasterio.float32), 1)

    def create_test_tiles(self):
        """Create test Tile objects with geometries that will intersect with our raster data."""

        # Create 5x5m tiles that overlap with rasters
        tile1 = Tile.objects.create(geometry=Polygon.from_bbox((25, 25, 30, 30)))
        tile2 = Tile.objects.create(geometry=Polygon.from_bbox((40, 40, 45, 45)))
        tile3 = Tile.objects.create(geometry=Polygon.from_bbox((45, 70, 50, 75)))
        tile4 = Tile.objects.cr < eate(
            geometry=Polygon.from_bbox((35, 35, 45, 45)),
            details=json.dumps({"top5_land_use": {"Friches": 10}}),
        )
        tile5 = Tile.objects.create(geometry=Polygon.from_bbox((5, 5, 10, 10)))

        return [tile1.id, tile2.id, tile3.id, tile4.id, tile5.id]

    def test_process_tile_batch(self):
        """Test that process_tile_batch correctly processes tiles and updates their details."""
        process_tile_batch(self.tiles, self.raster_files, self.raster_path)

        updated_tiles = Tile.objects.filter(id__in=[tile.id for tile in self.tiles])

        for tile in updated_tiles:
            details = json.loads(tile.details) if tile.details else {}
            self.assertIn("top5_land_use", details)
            if tile.id == self.tiles[1].id:
                self.assertIn("Bâtiments", details["top5_land_use"])
                self.assertGreater(details["top5_land_use"]["Bâtiments"], 0)
            elif tile.id == self.tiles[2].id:
                self.assertIn("Parking", details["top5_land_use"])
                self.assertGreater(details["top5_land_use"]["Parking"], 0)
            elif tile.id == self.tiles[3].id:
                self.assertIn("Giratoires", details["top5_land_use"])
                self.assertGreater(details["top5_land_use"]["Giratoires"], 0)
            elif tile.id == self.tiles[3].id:
                # Multiple land uses
                land_uses = list(details["top5_land_use"].keys())
                self.assertGreaterEqual(len(land_uses), 1)
            elif tile.id == self.tiles[4].id:
                # Outside tile
                self.assertEqual(details["top5_land_use"], {})
