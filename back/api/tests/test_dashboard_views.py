from django.contrib.gis.geos import Polygon
from django.test import SimpleTestCase, TestCase, Client, override_settings
from django.urls import reverse

from api.views.dashboard_views import _avg_from_counts, _safe_round
from iarbre_data.settings import SRID_DB
from iarbre_data.factories import (
    BiosphereFunctionalIntegrityFactory,
    CityFactory,
    DataFactory,
    IrisFactory,
    LczFactory,
    VegestrateFactory,
    VulnerabilityFactory,
)

VILLARD_SQUARE = Polygon(
    (
        (898233, 6441266),
        (903233, 6441266),
        (903233, 6446266),
        (898233, 6446266),
        (898233, 6441266),
    ),
    srid=SRID_DB,
)

NO_CACHE = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}


@override_settings(CACHES=NO_CACHE)
class DashboardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("dashboard")
        self.city = CityFactory(
            code="38250",
            name="Villard-de-Lans",
            geometry=VILLARD_SQUARE,
            plantability_counts={"0": 10, "2": 20, "4": 30, "6": 40, "8": 50, "10": 60},
        )
        self.iris = IrisFactory(
            code="382500101",
            name="Centre",
            city=self.city,
            geometry=VILLARD_SQUARE,
            plantability_counts={"2": 10, "8": 10},
        )
        VulnerabilityFactory(
            geometry=VILLARD_SQUARE,
            vulnerability_index_day=6.0,
            vulnerability_index_night=4.0,
            expo_index_day=2.0,
            expo_index_night=1.0,
            sensibilty_index_day=2.0,
            sensibilty_index_night=1.5,
            capaf_index_day=2.0,
            capaf_index_night=1.5,
        )
        LczFactory(
            geometry=VILLARD_SQUARE,
            lcz_index="2",
            details={
                "hre": 15.0,
                "bur": 20.0,
                "ror": 30.0,
                "bsr": 5.0,
                "ver": 40.0,
                "war": 5.0,
                "vhr": 25.0,
            },
        )
        VegestrateFactory(
            geometry=VILLARD_SQUARE, strate="arborescent", surface=500_000
        )
        VegestrateFactory(geometry=VILLARD_SQUARE, strate="arbustif", surface=200_000)
        VegestrateFactory(geometry=VILLARD_SQUARE, strate="herbacee", surface=300_000)
        DataFactory(geometry=VILLARD_SQUARE, factor="Bâtiments")
        BiosphereFunctionalIntegrityFactory(geometry=VILLARD_SQUARE, indice=70)

    def test_metropole_returns_structure(self):
        data = self.client.get(self.url).json()
        self.assertIsNone(data["city"])
        for key in [
            "areaHa",
            "plantability",
            "vulnerability",
            "vegetation",
            "lcz",
            "buildings",
            "biosphere",
        ]:
            self.assertIn(key, data)

    def test_metropole_plantability(self):
        data = self.client.get(self.url).json()
        plantability = data["plantability"]
        self.assertAlmostEqual(plantability["averageNormalizedIndice"], 6.7, places=1)
        divisions = plantability["distributionByDivision"]
        self.assertEqual(len(divisions), 1)
        self.assertEqual(divisions[0]["code"], "38250")

    def test_city_filter(self):
        data = self.client.get(self.url, {"city_code": "38250"}).json()
        self.assertEqual(data["city"]["code"], "38250")
        self.assertEqual(data["city"]["name"], "Villard-de-Lans")
        divisions = data["plantability"]["distributionByDivision"]
        self.assertEqual(len(divisions), 1)
        self.assertEqual(divisions[0]["code"], "382500101")

    def test_iris_filter(self):
        data = self.client.get(self.url, {"iris_code": "382500101"}).json()
        self.assertEqual(data["city"]["code"], "38250")
        self.assertEqual(data["plantability"]["distributionByDivision"], [])
        self.assertAlmostEqual(data["plantability"]["averageNormalizedIndice"], 5.0)

    def test_iris_code_priority_over_city_code(self):
        data = self.client.get(
            self.url, {"city_code": "38250", "iris_code": "382500101"}
        ).json()
        self.assertEqual(data["plantability"]["distributionByDivision"], [])

    def test_invalid_codes_return_404(self):
        self.assertEqual(
            self.client.get(self.url, {"city_code": "99999"}).status_code, 404
        )
        self.assertEqual(
            self.client.get(self.url, {"iris_code": "999999999"}).status_code, 404
        )

    def test_vulnerability_values(self):
        data = self.client.get(self.url).json()
        vuln = data["vulnerability"]
        self.assertEqual(vuln["averageDay"], 6.0)
        self.assertEqual(vuln["averageNight"], 4.0)
        self.assertEqual(vuln["expoDay"], 2.0)
        self.assertEqual(vuln["expoNight"], 1.0)

    def test_vegetation_values(self):
        data = self.client.get(self.url).json()
        veg = data["vegetation"]
        self.assertEqual(veg["totalm2"], 1000000.0)
        self.assertEqual(veg["treesSurfaceM2"], 500000.0)
        self.assertEqual(veg["bushesSurfaceM2"], 200000.0)
        self.assertEqual(veg["grassSurfaceM2"], 300000.0)

    def test_lcz_values(self):
        data = self.client.get(self.url).json()
        lcz = data["lcz"]
        self.assertEqual(lcz["averageBuildingSurfaceRate"], 20.0)
        self.assertEqual(lcz["averageBuildingHeight"], 15.0)
        self.assertEqual(lcz["impermeableSurfaceRate"], 30.0)
        self.assertEqual(lcz["totalVegetationRate"], 40.0)


@override_settings(CACHES=NO_CACHE)
class DashboardEmptyDataTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("dashboard")
        CityFactory(code="38250", name="Villard-de-Lans", geometry=VILLARD_SQUARE)

    def test_missing_data_returns_zeros(self):
        data = self.client.get(self.url, {"city_code": "38250"}).json()
        self.assertEqual(data["vulnerability"]["averageDay"], 0)
        self.assertEqual(data["lcz"]["averageBuildingSurfaceRate"], 0)
        self.assertEqual(data["vegetation"]["totalm2"], 0)
        self.assertEqual(data["buildings"]["averageBuildingFootprintM2"], 0)
        self.assertEqual(data["biosphere"]["averageIndice"], 0)


class HelperFunctionsTest(SimpleTestCase):
    def test_safe_round_none_returns_zero(self):
        self.assertEqual(_safe_round(None), 0)

    def test_safe_round_value(self):
        self.assertEqual(_safe_round(6.666), 6.7)

    def test_avg_from_counts_empty(self):
        self.assertEqual(_avg_from_counts({}), 0.0)

    def test_avg_from_counts_weighted(self):
        self.assertAlmostEqual(_avg_from_counts({"0": 1, "10": 1}), 5.0)

    def test_avg_from_counts_realistic(self):
        counts = {"0": 10, "2": 20, "4": 30, "6": 40, "8": 50, "10": 60}
        self.assertAlmostEqual(_avg_from_counts(counts), 6.667, places=2)
