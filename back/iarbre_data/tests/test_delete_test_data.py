from django.contrib.gis.geos import Polygon
from django.core.management import call_command
from django.test import TestCase

from iarbre_data.management.commands.populate import CITY_CODE
from iarbre_data.models import City, Data, Iris, Lcz, MVTTile, Tile, Vulnerability


class DeleteTestDataTest(TestCase):
    def setUp(self):
        # Test city centered at the populate.py coordinates
        self.test_geometry = Polygon.from_bbox((898000, 6441000, 903000, 6446000))
        self.test_city = City.objects.create(
            name="Villard-de-Lans",
            code=CITY_CODE,
            geometry=self.test_geometry,
        )
        self.test_iris = Iris.objects.create(
            name="test-iris",
            code="38250-iris",
            geometry=self.test_geometry,
            city=self.test_city,
        )
        self.test_tile = Tile.objects.create(
            geometry=self.test_geometry, city=self.test_city, iris=self.test_iris
        )
        self.test_lcz = Lcz.objects.create(geometry=self.test_geometry, lcz_index="1")
        self.test_vuln = Vulnerability.objects.create(
            geometry=self.test_geometry, vulnerability_index_day=1
        )
        self.test_qpv = Data.objects.create(geometry=self.test_geometry, factor="QPV")
        self.test_mvt = MVTTile.objects.create(
            zoom_level=13, tile_x=0, tile_y=0, geolevel="tile", datatype="tile"
        )

        # Real production data far from Villard-de-Lans (Lyon area)
        self.real_geometry = Polygon.from_bbox((840000, 6510000, 850000, 6520000))
        self.real_city = City.objects.create(
            name="Lyon", code="69123", geometry=self.real_geometry
        )
        self.real_lcz = Lcz.objects.create(geometry=self.real_geometry, lcz_index="2")
        self.real_vuln = Vulnerability.objects.create(
            geometry=self.real_geometry, vulnerability_index_day=2
        )
        self.real_qpv = Data.objects.create(geometry=self.real_geometry, factor="QPV")

    def test_deletes_test_city_and_related(self):
        call_command("delete_test_data")

        self.assertFalse(City.objects.filter(code=CITY_CODE).exists())
        self.assertFalse(Iris.objects.filter(pk=self.test_iris.pk).exists())
        self.assertFalse(Tile.objects.filter(pk=self.test_tile.pk).exists())
        self.assertFalse(Lcz.objects.filter(pk=self.test_lcz.pk).exists())
        self.assertFalse(Vulnerability.objects.filter(pk=self.test_vuln.pk).exists())
        self.assertFalse(Data.objects.filter(pk=self.test_qpv.pk).exists())

    def test_preserves_real_data_outside_test_area(self):
        call_command("delete_test_data")

        self.assertTrue(City.objects.filter(pk=self.real_city.pk).exists())
        self.assertTrue(Lcz.objects.filter(pk=self.real_lcz.pk).exists())
        self.assertTrue(Vulnerability.objects.filter(pk=self.real_vuln.pk).exists())
        self.assertTrue(Data.objects.filter(pk=self.real_qpv.pk).exists())

    def test_wipes_all_mvt_tiles(self):
        call_command("delete_test_data")

        self.assertFalse(MVTTile.objects.exists())

    def test_no_op_when_no_test_city(self):
        self.test_city.delete()

        call_command("delete_test_data")

        self.assertTrue(City.objects.filter(pk=self.real_city.pk).exists())
