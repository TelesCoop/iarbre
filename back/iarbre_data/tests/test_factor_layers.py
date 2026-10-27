from django.test import SimpleTestCase

from iarbre_data.data_config import FACTORS, FINE_GRID_FACTORS
from iarbre_data.utils.factor_layers import LAYER_QUERYSETS, get_factor_layers
from iarbre_data.utils.factor_margin import LEGACY_GRID_SIZE


class FactorLayersTestCase(SimpleTestCase):
    def test_legacy_grid_uses_data_factor(self):
        for factor_name in FACTORS:
            self.assertEqual(
                get_factor_layers(factor_name, LEGACY_GRID_SIZE),
                ([("data", factor_name)], []),
            )

    def test_fine_grid_uses_composition(self):
        self.assertEqual(
            get_factor_layers("Strate arborée", 1),
            ([("vegestrate", "arborescent")], []),
        )
        self.assertEqual(
            get_factor_layers("Bâtiments", 1), ([("data", "Bâtiments")], [])
        )

    def test_fine_grid_layers_are_known(self):
        for factor_name, layers in FINE_GRID_FACTORS.items():
            self.assertIn(factor_name, FACTORS)
            for kind, _ in layers["include"] + layers.get("exclude", []):
                self.assertIn(kind, LAYER_QUERYSETS)
