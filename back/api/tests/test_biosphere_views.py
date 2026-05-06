from django.contrib.gis.geos import Polygon
from django.test import Client, TestCase
from django.urls import reverse

from iarbre_data.models import BiosphereFunctionalIntegrityLandCover
from iarbre_data.settings import SRID_DB
from iarbre_data.utils.biosphere_land_cover import LandCoverClass


class BiosphereLandCoverAtPointViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        lyon_square = Polygon(
            (
                (840000, 6520000),
                (855000, 6520000),
                (855000, 6535000),
                (840000, 6535000),
                (840000, 6520000),
            ),
            srid=SRID_DB,
        )
        self.record = BiosphereFunctionalIntegrityLandCover.objects.create(
            geometry=lyon_square,
            land_cover=LandCoverClass.FEUILLU,
            binary=True,
        )
        self.url = reverse("biosphere-land-cover-at-point")

    def test_valid_point_returns_land_cover(self):
        response = self.client.get(self.url, {"lat": 45.8095, "lng": 4.8677})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["landCover"], LandCoverClass.FEUILLU)
        self.assertEqual(data[0]["landCoverLabel"], "Feuillu")
        self.assertEqual(data[0]["binary"], True)

    def test_point_outside_coverage_returns_empty(self):
        response = self.client.get(self.url, {"lat": 48.8566, "lng": 2.3522})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
