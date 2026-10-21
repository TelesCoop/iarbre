from django.contrib.gis.geos import Point
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from iarbre_data.factories import PublicBuildingFactory
from iarbre_data.models import PublicBuilding
from iarbre_data.settings import SRID_DB


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)
class PublicBuildingListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        PublicBuildingFactory(
            nature_detaillee="Ecole élémentaire",
            name="École Saint-Exupéry",
            uai="0690163C",
            student_count=250,
            education_priority="REP+",
        )
        PublicBuildingFactory(
            geometry=Point(843000, 6520000, srid=SRID_DB),
            category=PublicBuilding.Category.SANTE,
            nature="Hôpital",
            fictif=True,
        )

    def test_returns_geojson_feature_collection(self):
        response = self.client.get(reverse("public-buildings-list"))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["type"], "FeatureCollection")
        self.assertEqual(len(data["features"]), 2)

    def test_features_have_expected_properties(self):
        response = self.client.get(reverse("public-buildings-list"))

        features = {f["properties"]["category"]: f for f in response.json()["features"]}
        school = features["enseignement"]
        self.assertEqual(school["geometry"]["type"], "Polygon")
        self.assertEqual(school["properties"]["name"], "École Saint-Exupéry")
        self.assertEqual(school["properties"]["studentCount"], 250)
        self.assertEqual(school["properties"]["educationPriority"], "REP+")
        self.assertNotIn("uai", school["properties"])
        hospital = features["sante"]
        self.assertEqual(hospital["geometry"]["type"], "Point")
        lon, lat = hospital["geometry"]["coordinates"]
        self.assertAlmostEqual(lon, 4.8, delta=0.3)
        self.assertAlmostEqual(lat, 45.7, delta=0.3)
        self.assertEqual(round(lon, 6), lon)
