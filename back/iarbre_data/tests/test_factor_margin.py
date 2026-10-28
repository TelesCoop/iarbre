from django.test import SimpleTestCase

from iarbre_data.data_config import BLOCKING_SCORE, FACTORS
from iarbre_data.utils.factor_margin import (
    LEGACY_GRID_SIZE,
    get_factor_margin,
    get_factor_uncertainty,
)


class FactorMarginTestCase(SimpleTestCase):
    def test_legacy_grid_has_no_margin(self):
        for factor_name in FACTORS:
            self.assertEqual(get_factor_margin(factor_name, LEGACY_GRID_SIZE), 0)

    def test_fine_grid_margin(self):
        for factor_name, weight in FACTORS.items():
            margin = get_factor_margin(factor_name, 1)
            if weight == BLOCKING_SCORE:
                self.assertEqual(margin, get_factor_uncertainty(factor_name))
            else:
                self.assertEqual(margin, 0)
