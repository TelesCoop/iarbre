from django.contrib.gis.geos import Polygon
from django.test import TestCase

from iarbre_data.models import Tile
from iarbre_data.settings import SRID_DB
from plantability.management.commands.compute_meta_factors_avg import (
    _compute_meta_factors_avg,
)

SIMPLE_SQUARE = Polygon(
    (
        (898233, 6441266),
        (903233, 6441266),
        (903233, 6446266),
        (898233, 6446266),
        (898233, 6441266),
    ),
    srid=SRID_DB,
)


class ComputeMetaFactorsAvgTest(TestCase):
    def _tile(self, meta_factors):
        return Tile.objects.create(geometry=SIMPLE_SQUARE, meta_factors=meta_factors)

    def test_empty_queryset_returns_none(self):
        self.assertIsNone(_compute_meta_factors_avg(Tile.objects.none()))

    def test_all_null_meta_factors_returns_none(self):
        self._tile(None)
        self._tile(None)
        self.assertIsNone(_compute_meta_factors_avg(Tile.objects.all()))

    def test_nested_structure_computes_averages(self):
        self._tile({"meta_factors": {"eau": 0.4, "bati": 0.6}})
        self._tile({"meta_factors": {"eau": 0.8, "bati": 0.2}})
        result = _compute_meta_factors_avg(Tile.objects.all())
        self.assertAlmostEqual(result["eau"], 0.6, places=4)
        self.assertAlmostEqual(result["bati"], 0.4, places=4)

    def test_flat_structure_returns_empty_dict(self):
        self._tile({"eau": 0.5, "bati": 0.3})
        result = _compute_meta_factors_avg(Tile.objects.all())
        self.assertEqual(result, {})

    def test_absent_key_dilutes_average(self):
        self._tile({"meta_factors": {"eau": 0.8}})
        self._tile({"meta_factors": {}})
        result = _compute_meta_factors_avg(Tile.objects.all())
        self.assertAlmostEqual(result["eau"], 0.4, places=4)

    def test_single_tile_returns_exact_values(self):
        self._tile({"meta_factors": {"foret": 0.75}})
        result = _compute_meta_factors_avg(Tile.objects.all())
        self.assertEqual(result, {"foret": 0.75})
