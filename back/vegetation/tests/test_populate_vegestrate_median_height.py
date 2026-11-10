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
from vegetation.management.commands.populate_vegestrate_median_height import (
    compute_median_heights,
    save_median_heights,
)


class PopulateVegestrateMedianHeightTest(TestCase):
    def setUp(self):
        Vegestrate.objects.all().delete()

    def test_computes_and_saves_median_height_across_strips(self):
        veg = Vegestrate.objects.create(
            geometry=GEOSGeometry(
                "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))", srid=SRID_DB
            ),
            strate="arborescent",
            surface=100.0,
        )

        medians = compute_median_heights(self._make_raster(), strip_height=5)
        self.assertEqual(medians[veg.id], 2.0)

        save_median_heights(medians)
        veg.refresh_from_db()
        self.assertEqual(veg.median_height, 2.0)

    def test_polygon_outside_raster_keeps_null_median_height(self):
        outside = Vegestrate.objects.create(
            geometry=GEOSGeometry(
                "POLYGON((500 500, 510 500, 510 510, 500 510, 500 500))", srid=SRID_DB
            ),
            surface=100.0,
        )

        medians = compute_median_heights(self._make_raster(), strip_height=5)
        self.assertNotIn(outside.id, medians)

        save_median_heights(medians)
        outside.refresh_from_db()
        self.assertIsNone(outside.median_height)

    def _make_raster(self):
        tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmpdir)
        path = os.path.join(tmpdir, "test_vegestrate_elevation.tif")
        transform = from_origin(0, 10, 1, 1)
        data = np.full((10, 10), 2, dtype=np.int16)
        data[:, 7:] = 30
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
