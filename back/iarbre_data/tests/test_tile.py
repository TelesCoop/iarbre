from django.test import TestCase
from django.contrib.gis.geos import Polygon
from iarbre_data.models import Tile, City, Iris
from iarbre_data.settings import TARGET_PROJ, TARGET_MAP_PROJ


class TileTest(TestCase):
    def setUp(self):
        self.city = City.objects.create(
            geometry=Polygon(((0, 0), (1, 1), (1, 0), (0, 0))),
            code="CITY123",
            name="Test City",
        )

        self.iris = Iris.objects.create(
            geometry=Polygon(((0, 0), (1, 1), (1, 0), (0, 0))),
            code="IRIS123",
            name="Test IRIS",
            city=self.city,
        )
        self.geometry = Polygon(
            ((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)), srid=TARGET_PROJ
        )  # Simple square polygon
        self.tile = Tile.objects.create(
            plantability_normalized_indice=0.5,
            plantability_indice=0.5,
            geometry=self.geometry,
            map_geometry=self.geometry.transform(TARGET_MAP_PROJ, clone=True),
            city_id=City.objects.first().id,
            iris_id=Iris.objects.first().id,
        )

    def test_geometry_field(self):
        """Test that geometry field works as expected."""
        self.assertEqual(self.tile.geometry.wkt, self.geometry.wkt)
