import os
import shutil
import tempfile

import numpy as np
import rasterio
from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase
from rasterio.transform import from_origin

from iarbre_data.models import Vegestrate
from iarbre_data.settings import SRID_DB
from vegetation.management.commands.populate_vegestrate_mean_height import (
    compute_sums_and_counts,
    save_mean_heights,
)


class PopulateVegestrateMeanHeightTest(TestCase):
    def setUp(self):
        Vegestrate.objects.all().delete()

    def test_computes_and_saves_mean_height(self):
        veg = Vegestrate.objects.create(
            geometry=GEOSGeometry(
                "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))", srid=SRID_DB
            ),
            strate="arborescent",
            surface=100.0,
        )

        raster_path = self._make_raster()
        sums, counts = compute_sums_and_counts(raster_path, strip_height=5)
        self.assertEqual(counts[veg.id], 100)
        self.assertEqual(sums[veg.id], 10.0 * 100)

        save_mean_heights(sums, counts)
        veg.refresh_from_db()
        self.assertEqual(veg.mean_height, 10.0)

    def test_polygon_outside_raster_keeps_null_mean_height(self):
        outside = Vegestrate.objects.create(
            geometry=GEOSGeometry(
                "POLYGON((500 500, 510 500, 510 510, 500 510, 500 500))", srid=SRID_DB
            ),
            surface=100.0,
        )

        sums, counts = compute_sums_and_counts(self._make_raster(), strip_height=5)
        self.assertNotIn(outside.id, sums)

        save_mean_heights(sums, counts)
        outside.refresh_from_db()
        self.assertIsNone(outside.mean_height)

    def _make_raster(self):
        tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmpdir)
        path = os.path.join(tmpdir, "test_vegestrate_elevation.tif")
        transform = from_origin(0, 10, 1, 1)
        data = np.full((10, 10), 10, dtype=np.int16)
        with rasterio.open(
            path,
            "w",
            driver="GTiff",
            height=10,
            width=10,
            count=1,
            dtype=np.int16,
            crs=f"EPSG:{SRID_DB}",
            transform=transform,
            nodata=-9999,
        ) as dst:
            dst.write(data, 1)
        return path
