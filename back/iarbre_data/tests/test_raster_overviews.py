import os
import shutil
import tempfile
from io import StringIO
from pathlib import Path

import numpy as np
import rasterio
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings
from rasterio.enums import Resampling
from rasterio.transform import from_bounds

from iarbre_data.utils.raster_overviews import (
    build_overviews,
    overview_factors,
    ovr_path,
)


def _write_raster(path: Path, size: int) -> None:
    data = (np.arange(size * size) % 251).astype(np.uint8).reshape(size, size)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=size,
        width=size,
        count=1,
        dtype="uint8",
        crs="EPSG:2154",
        transform=from_bounds(840000, 6510000, 850000, 6520000, size, size),
        nodata=0,
        compress="lzw",
    ) as dst:
        dst.write(data, 1)


class OverviewFactorsTest(SimpleTestCase):
    def test_factors_stop_at_min_size(self):
        self.assertEqual(overview_factors(5744, 8488), [2, 4, 8, 16])

    def test_no_factor_for_small_raster(self):
        self.assertEqual(overview_factors(300, 300), [])


class BuildOverviewsTest(SimpleTestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.path = self.tmp_dir / "layer.tif"
        _write_raster(self.path, 1024)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_builds_external_overviews(self):
        original = self.path.read_bytes()

        self.assertTrue(build_overviews(self.path))

        self.assertTrue(ovr_path(self.path).exists())
        self.assertEqual(self.path.read_bytes(), original)
        with rasterio.open(self.path) as src:
            self.assertEqual(src.overviews(1), [2, 4])

    def test_overview_read_matches_nearest_decimation(self):
        build_overviews(self.path)

        with rasterio.open(self.path) as src:
            full = src.read(1)
            reduced = src.read(1, out_shape=(256, 256), resampling=Resampling.nearest)
        np.testing.assert_array_equal(reduced, full[::4, ::4])

    def test_leaves_no_temporary_files(self):
        build_overviews(self.path)

        self.assertEqual(
            sorted(p.name for p in self.tmp_dir.iterdir()),
            ["layer.tif", "layer.tif.ovr"],
        )

    def test_skips_when_up_to_date(self):
        build_overviews(self.path)

        self.assertFalse(build_overviews(self.path))

    def test_rebuilds_when_raster_is_newer(self):
        build_overviews(self.path)
        ovr_mtime = ovr_path(self.path).stat().st_mtime
        os.utime(self.path, (ovr_mtime + 10, ovr_mtime + 10))

        self.assertTrue(build_overviews(self.path))

    def test_force_rebuilds(self):
        build_overviews(self.path)

        self.assertTrue(build_overviews(self.path, force=True))

    def test_skips_small_raster(self):
        small = self.tmp_dir / "small.tif"
        _write_raster(small, 300)

        self.assertFalse(build_overviews(small))
        self.assertFalse(ovr_path(small).exists())


class BuildWmsOverviewsCommandTest(SimpleTestCase):
    def setUp(self):
        self.media_dir = Path(tempfile.mkdtemp())
        self.wms_dir = self.media_dir / "rasters" / "WMS"
        self.wms_dir.mkdir(parents=True)
        _write_raster(self.wms_dir / "layer.tif", 1024)

    def tearDown(self):
        shutil.rmtree(self.media_dir, ignore_errors=True)

    def test_command_builds_then_skips(self):
        with override_settings(MEDIA_ROOT=str(self.media_dir)):
            first = StringIO()
            call_command("build_wms_overviews", stdout=first)
            second = StringIO()
            call_command("build_wms_overviews", stdout=second)

        self.assertIn("layer.tif built", first.getvalue())
        self.assertIn("layer.tif skipped", second.getvalue())
        self.assertTrue((self.wms_dir / "layer.tif.ovr").exists())
