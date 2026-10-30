from django.test import SimpleTestCase

from iarbre_data.utils.factor_layers import get_factor_layers
from iarbre_data.utils.factor_margin import LEGACY_GRID_SIZE


class FactorLayersTestCase(SimpleTestCase):
    def test_fine_grid_uses_composition(self):
        self.assertEqual(
            get_factor_layers("Strate arborée", 1),
            ([("vegestrate", "arborescent")], []),
        )
        self.assertEqual(
            get_factor_layers("Strate arborée", LEGACY_GRID_SIZE),
            ([("data", "Strate arborée")], []),
        )
        self.assertEqual(
            get_factor_layers("Bâtiments", 1), ([("data", "Bâtiments")], [])
        )
