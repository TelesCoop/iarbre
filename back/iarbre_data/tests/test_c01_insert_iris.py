from django.test import TestCase

from iarbre_data.factories import CityFactory, IrisFactory, TileFactory
from iarbre_data.management.commands.c01_insert_cities_and_iris import (
    iris_from_feature,
    remove_stale_iris,
)
from iarbre_data.models import Iris, Tile
from iarbre_data.settings import SRID_DB


class IrisFromFeatureTest(TestCase):
    def test_keeps_largest_part_of_multipolygon(self):
        small = [
            [842000, 6518500],
            [842010, 6518500],
            [842010, 6518510],
            [842000, 6518510],
            [842000, 6518500],
        ]
        large = [
            [843000, 6518500],
            [843500, 6518500],
            [843500, 6519000],
            [843000, 6519000],
            [843000, 6518500],
        ]
        feature = {
            "type": "Feature",
            "geometry": {"type": "MultiPolygon", "coordinates": [[small], [large]]},
            "properties": {
                "code_insee": "69382",
                "code_iris": "693820202",
                "nom_iris": "Bellecour-A Gourjus",
            },
        }

        code, name, geom = iris_from_feature(feature)

        self.assertEqual(code, "693820202")
        self.assertEqual(name, "Bellecour-A Gourjus")
        self.assertEqual(geom.geom_type, "Polygon")
        self.assertEqual(geom.srid, SRID_DB)
        self.assertEqual(geom.area, 500 * 500)


class RemoveStaleIrisTest(TestCase):
    def setUp(self):
        self.city = CityFactory(code="69382")
        self.kept = IrisFactory(code="693820202", city=self.city)
        self.stale = IrisFactory(code="693820999", city=self.city)
        self.other_city_iris = IrisFactory(code="693850101", city=CityFactory())
        self.tile = TileFactory(iris=self.stale, city=self.city)

    def test_deletes_iris_missing_from_ign_and_keeps_their_tiles(self):
        remove_stale_iris(self.city, ["693820202"])

        self.assertQuerySetEqual(
            Iris.objects.order_by("code"),
            [self.kept, self.other_city_iris],
        )
        self.tile.refresh_from_db()
        self.assertIsNone(self.tile.iris)

    def test_keeps_everything_when_ign_returns_nothing(self):
        remove_stale_iris(self.city, [])

        self.assertEqual(Iris.objects.count(), 3)
        self.assertTrue(Tile.objects.filter(iris=self.stale).exists())
