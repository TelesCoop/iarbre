import random
from django.test import TestCase

from iarbre_data.factories import TileFactory, TileFactorsFactory
from iarbre_data.models import Tile
from iarbre_data.data_config import FACTORS
from plantability.management.commands.c01_compute_plantability_indice import (
    compute_indice,
    compute_normalized_indice,
)


class C01ComputePlantabilityTestCase(TestCase):
    def setUp(self):
        factors_names = list(FACTORS.keys())
        TileFactory.create_batch(50)
        tiles = list(Tile.objects.all())
        for idx in range(4):
            for _ in range(5):
                TileFactorsFactory.create(
                    tile=random.choice(tiles), factor=factors_names[idx]
                )

    def test_compute_indice(self):
        qs = Tile.objects.all()
        tiles_id = list(qs.values_list("id", flat=True))
        tiles_plantability = list(qs.values_list("plantability_indice", flat=True))
        compute_indice(tiles_id)
        self.assertNotEquals(
            list(Tile.objects.all().values_list("plantability_indice", flat=True)),
            tiles_plantability,
        )

    def test_compute_normalized_indice(self):
        qs = Tile.objects.all()
        tiles_plantability = list(
            qs.values_list("plantability_normalized_indice", flat=True)
        )
        compute_normalized_indice()
        self.assertNotEquals(
            list(
                Tile.objects.all().values_list(
                    "plantability_normalized_indice", flat=True
                )
            ),
            tiles_plantability,
        )
