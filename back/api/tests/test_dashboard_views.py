from django.contrib.gis.geos import Polygon
from django.test import SimpleTestCase, TestCase, Client, override_settings
from django.urls import reverse

from api.views.dashboard_views import _avg_from_counts, _m2_to_ha, _safe_round
from iarbre_data.factories import (
    CityFactory,
    IrisFactory,
    LczFactory,
    VegestrateFactory,
    VulnerabilityFactory,
)

GEOM = Polygon(
    (
        (845000, 6525000),
        (845100, 6525000),
        (845100, 6525100),
        (845000, 6525100),
        (845000, 6525000),
    ),
    srid=2154,
)

NO_CACHE = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}


@override_settings(CACHES=NO_CACHE)
class DashboardViewMetropoleTest(TestCase):
    """Tests for the dashboard at metropole level (no query params)."""

    @classmethod
    def setUpTestData(cls):
        cls.city = CityFactory(
            code="69123",
            name="Lyon",
            geometry=GEOM,
            plantability_counts={"0": 10, "2": 20, "4": 30, "6": 40, "8": 50, "10": 60},
        )
        cls.iris = IrisFactory(
            code="691230101", name="Presqu'ile", city=cls.city, geometry=GEOM
        )

        VulnerabilityFactory(
            geometry=GEOM,
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
            geometry=GEOM,
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
        LczFactory(
            geometry=GEOM,
            lcz_index="A",
            details={
                "hre": 0.0,
                "bur": 0.0,
                "ror": 5.0,
                "bsr": 10.0,
                "ver": 80.0,
                "war": 5.0,
                "vhr": 60.0,
            },
        )

        VegestrateFactory(geometry=GEOM, strate="arborescent", surface=500_000)
        VegestrateFactory(geometry=GEOM, strate="arbustif", surface=200_000)
        VegestrateFactory(geometry=GEOM, strate="herbacee", surface=300_000)

    def setUp(self):
        self.client = Client()
        self.url = reverse("dashboard")

    def test_metropole_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_metropole_response_structure(self):
        response = self.client.get(self.url)
        data = response.json()

        self.assertIsNone(data["city"])
        self.assertIn("areaHa", data)
        self.assertIn("plantability", data)
        self.assertIn("vulnerability", data)
        self.assertIn("vegetation", data)
        self.assertIn("lcz", data)

    def test_metropole_plantability_structure(self):
        data = self.client.get(self.url).json()
        plantability = data["plantability"]

        self.assertIn("averageNormalizedIndice", plantability)
        self.assertIn("distribution", plantability)
        self.assertIn("distributionByDivision", plantability)
        self.assertIsInstance(plantability["distributionByDivision"], list)
        self.assertGreater(len(plantability["distributionByDivision"]), 0)

    def test_metropole_plantability_average(self):
        """Average from plantability_counts: (0*10+2*20+4*30+6*40+8*50+10*60)/210 ≈ 6.7."""
        data = self.client.get(self.url).json()
        avg = data["plantability"]["averageNormalizedIndice"]
        self.assertAlmostEqual(avg, 6.7, places=1)

    def test_metropole_vulnerability_values(self):
        data = self.client.get(self.url).json()
        vuln = data["vulnerability"]

        self.assertEqual(vuln["averageDay"], 6.0)
        self.assertEqual(vuln["averageNight"], 4.0)
        self.assertEqual(vuln["expoDay"], 2.0)
        self.assertEqual(vuln["expoNight"], 1.0)
        self.assertEqual(vuln["sensibilityDay"], 2.0)
        self.assertEqual(vuln["sensibilityNight"], 1.5)
        self.assertEqual(vuln["capafDay"], 2.0)
        self.assertEqual(vuln["capafNight"], 1.5)

    def test_metropole_vegetation_values(self):
        data = self.client.get(self.url).json()
        veg = data["vegetation"]

        self.assertEqual(veg["totalHa"], 100.0)
        self.assertEqual(veg["treesSurfaceHa"], 50.0)
        self.assertEqual(veg["bushesSurfaceHa"], 20.0)
        self.assertEqual(veg["grassSurfaceHa"], 30.0)

    def test_metropole_lcz_structure(self):
        data = self.client.get(self.url).json()
        lcz = data["lcz"]

        expected_keys = [
            "averageBuildingSurfaceRate",
            "averageBuildingHeight",
            "impermeableSurfaceRate",
            "permeableSoilRate",
            "buildingRate",
            "treeCoverRate",
            "totalVegetationRate",
            "waterRate",
        ]
        for key in expected_keys:
            self.assertIn(key, lcz)

    def test_metropole_lcz_building_avg_uses_built_only(self):
        """Building metrics should average only built LCZ (index '2'), not natural (index 'A')."""
        data = self.client.get(self.url).json()
        lcz = data["lcz"]

        self.assertEqual(lcz["averageBuildingSurfaceRate"], 20.0)
        self.assertEqual(lcz["averageBuildingHeight"], 15.0)

    def test_metropole_lcz_surface_avg_uses_all(self):
        """Surface rates should average all LCZ (both '2' and 'A')."""
        data = self.client.get(self.url).json()
        lcz = data["lcz"]

        self.assertEqual(lcz["impermeableSurfaceRate"], 17.5)
        self.assertEqual(lcz["totalVegetationRate"], 60.0)
        self.assertEqual(lcz["treeCoverRate"], 42.5)
        self.assertEqual(lcz["buildingRate"], 10.0)

    def test_metropole_division_entries(self):
        data = self.client.get(self.url).json()
        divisions = data["plantability"]["distributionByDivision"]

        self.assertEqual(len(divisions), 1)
        entry = divisions[0]
        self.assertEqual(entry["code"], "69123")
        self.assertEqual(entry["name"], "Lyon")
        self.assertIn("averageNormalizedIndice", entry)
        self.assertIn("distribution", entry)


@override_settings(CACHES=NO_CACHE)
class DashboardViewCityTest(TestCase):
    """Tests for the dashboard filtered by city_code."""

    @classmethod
    def setUpTestData(cls):
        cls.city = CityFactory(
            code="69123",
            name="Lyon",
            geometry=GEOM,
            plantability_counts={"0": 5, "2": 10, "4": 15, "6": 20, "8": 25, "10": 30},
        )
        cls.iris = IrisFactory(
            code="691230101", name="Presqu'ile", city=cls.city, geometry=GEOM
        )

        VulnerabilityFactory(
            geometry=GEOM,
            vulnerability_index_day=5.0,
            vulnerability_index_night=3.0,
            expo_index_day=1.5,
            expo_index_night=0.8,
            sensibilty_index_day=1.5,
            sensibilty_index_night=1.0,
            capaf_index_day=2.0,
            capaf_index_night=1.2,
        )

        LczFactory(
            geometry=GEOM,
            lcz_index="3",
            details={
                "hre": 10.0,
                "bur": 30.0,
                "ror": 25.0,
                "bsr": 5.0,
                "ver": 35.0,
                "war": 5.0,
                "vhr": 20.0,
            },
        )

        VegestrateFactory(geometry=GEOM, strate="arborescent", surface=100_000)
        VegestrateFactory(geometry=GEOM, strate="arbustif", surface=50_000)
        VegestrateFactory(geometry=GEOM, strate="herbacee", surface=75_000)

    def setUp(self):
        self.client = Client()
        self.url = reverse("dashboard")

    def test_city_filter_returns_200(self):
        response = self.client.get(self.url, {"city_code": "69123"})
        self.assertEqual(response.status_code, 200)

    def test_city_filter_returns_city_info(self):
        data = self.client.get(self.url, {"city_code": "69123"}).json()

        self.assertIsNotNone(data["city"])
        self.assertEqual(data["city"]["code"], "69123")
        self.assertEqual(data["city"]["name"], "Lyon")

    def test_city_filter_returns_city_vegetation(self):
        data = self.client.get(self.url, {"city_code": "69123"}).json()
        veg = data["vegetation"]

        self.assertEqual(veg["totalHa"], 22.5)
        self.assertEqual(veg["treesSurfaceHa"], 10.0)
        self.assertEqual(veg["bushesSurfaceHa"], 5.0)
        self.assertEqual(veg["grassSurfaceHa"], 7.5)

    def test_city_filter_plantability_has_iris_divisions(self):
        data = self.client.get(self.url, {"city_code": "69123"}).json()
        divisions = data["plantability"]["distributionByDivision"]

        self.assertEqual(len(divisions), 1)
        self.assertEqual(divisions[0]["code"], "691230101")

    def test_invalid_city_code_returns_404(self):
        response = self.client.get(self.url, {"city_code": "99999"})
        self.assertEqual(response.status_code, 404)


@override_settings(CACHES=NO_CACHE)
class DashboardViewIrisTest(TestCase):
    """Tests for the dashboard filtered by iris_code."""

    @classmethod
    def setUpTestData(cls):
        cls.city = CityFactory(
            code="69123",
            name="Lyon",
            geometry=GEOM,
        )
        cls.iris = IrisFactory(
            code="691230101", name="Presqu'ile", city=cls.city, geometry=GEOM
        )

        VegestrateFactory(geometry=GEOM, strate="arborescent", surface=100_000)
        VegestrateFactory(geometry=GEOM, strate="arbustif", surface=50_000)
        VegestrateFactory(geometry=GEOM, strate="herbacee", surface=75_000)

    def setUp(self):
        self.client = Client()
        self.url = reverse("dashboard")

    def test_iris_filter_returns_200(self):
        response = self.client.get(self.url, {"iris_code": "691230101"})
        self.assertEqual(response.status_code, 200)

    def test_iris_filter_returns_parent_city(self):
        data = self.client.get(self.url, {"iris_code": "691230101"}).json()

        self.assertIsNotNone(data["city"])
        self.assertEqual(data["city"]["code"], "69123")

    def test_iris_filter_has_no_subdivision(self):
        data = self.client.get(self.url, {"iris_code": "691230101"}).json()
        divisions = data["plantability"]["distributionByDivision"]

        self.assertEqual(divisions, [])

    def test_iris_vegetation_uses_spatial_filter(self):
        """IRIS-level vegetation uses Vegestrate spatial intersection."""
        data = self.client.get(self.url, {"iris_code": "691230101"}).json()
        veg = data["vegetation"]

        self.assertEqual(veg["totalHa"], 22.5)

    def test_invalid_iris_code_returns_404(self):
        response = self.client.get(self.url, {"iris_code": "999999999"})
        self.assertEqual(response.status_code, 404)


@override_settings(CACHES=NO_CACHE)
class DashboardViewEmptyDataTest(TestCase):
    """Tests for the dashboard with empty/missing data."""

    @classmethod
    def setUpTestData(cls):
        cls.city = CityFactory(
            code="69123",
            name="Lyon",
            geometry=GEOM,
        )

    def setUp(self):
        self.client = Client()
        self.url = reverse("dashboard")

    def test_no_tiles_returns_default_plantability(self):
        """With default_plantability_counts (NEUTRAL=1), average is 6.0."""
        data = self.client.get(self.url, {"city_code": "69123"}).json()
        self.assertEqual(data["plantability"]["averageNormalizedIndice"], 6.0)

    def test_no_vegestrate_returns_zero(self):
        data = self.client.get(self.url, {"city_code": "69123"}).json()
        veg = data["vegetation"]

        self.assertEqual(veg["totalHa"], 0)
        self.assertEqual(veg["treesSurfaceHa"], 0)
        self.assertEqual(veg["bushesSurfaceHa"], 0)
        self.assertEqual(veg["grassSurfaceHa"], 0)

    def test_no_vulnerability_returns_zeros(self):
        data = self.client.get(self.url, {"city_code": "69123"}).json()
        vuln = data["vulnerability"]

        self.assertEqual(vuln["averageDay"], 0)
        self.assertEqual(vuln["averageNight"], 0)

    def test_no_lcz_returns_zeros(self):
        data = self.client.get(self.url, {"city_code": "69123"}).json()
        lcz = data["lcz"]

        self.assertEqual(lcz["averageBuildingSurfaceRate"], 0)
        self.assertEqual(lcz["impermeableSurfaceRate"], 0)
        self.assertEqual(lcz["totalVegetationRate"], 0)


@override_settings(CACHES=NO_CACHE)
class DashboardViewLczPartitionTest(TestCase):
    """Tests that LCZ surface rates sum to 100% when individual zones do."""

    @classmethod
    def setUpTestData(cls):
        cls.city = CityFactory(code="69123", name="Lyon", geometry=GEOM)

        LczFactory(
            geometry=GEOM,
            lcz_index="2",
            details={
                "bur": 25.0,
                "ror": 35.0,
                "bsr": 5.0,
                "ver": 30.0,
                "war": 5.0,
                "vhr": 15.0,
                "hre": 12.0,
            },
        )
        LczFactory(
            geometry=GEOM,
            lcz_index="D",
            details={
                "bur": 0.0,
                "ror": 5.0,
                "bsr": 15.0,
                "ver": 75.0,
                "war": 5.0,
                "vhr": 50.0,
                "hre": 0.0,
            },
        )

    def setUp(self):
        self.client = Client()
        self.url = reverse("dashboard")

    def test_surface_rates_sum_to_100(self):
        data = self.client.get(self.url, {"city_code": "69123"}).json()
        lcz = data["lcz"]

        total = (
            lcz["buildingRate"]
            + lcz["impermeableSurfaceRate"]
            + lcz["permeableSoilRate"]
            + lcz["totalVegetationRate"]
            + lcz["waterRate"]
        )
        self.assertAlmostEqual(total, 100.0, places=1)


class HelperFunctionsTest(SimpleTestCase):
    """Unit tests for dashboard helper functions."""

    def test_safe_round_none_returns_zero(self):
        self.assertEqual(_safe_round(None), 0)

    def test_safe_round_value(self):
        self.assertEqual(_safe_round(6.666), 6.7)

    def test_safe_round_integer_value(self):
        self.assertEqual(_safe_round(5.0), 5.0)

    def test_m2_to_ha_normal(self):
        self.assertEqual(_m2_to_ha(50_000), 5.0)

    def test_m2_to_ha_zero(self):
        self.assertEqual(_m2_to_ha(0), 0)

    def test_m2_to_ha_rounds_to_one_decimal(self):
        self.assertEqual(_m2_to_ha(15_555), 1.6)

    def test_avg_from_counts_empty_dict(self):
        self.assertEqual(_avg_from_counts({}), 0.0)

    def test_avg_from_counts_all_zero_values(self):
        self.assertEqual(_avg_from_counts({"0": 0, "5": 0, "10": 0}), 0.0)

    def test_avg_from_counts_single_entry(self):
        self.assertEqual(_avg_from_counts({"10": 5}), 10.0)

    def test_avg_from_counts_weighted(self):
        result = _avg_from_counts({"0": 1, "10": 1})
        self.assertEqual(result, 5.0)

    def test_avg_from_counts_realistic(self):
        """(0*10 + 2*20 + 4*30 + 6*40 + 8*50 + 10*60) / 210 = 1400/210 ≈ 6.667."""
        counts = {"0": 10, "2": 20, "4": 30, "6": 40, "8": 50, "10": 60}
        self.assertAlmostEqual(_avg_from_counts(counts), 6.667, places=2)


GEOM_B = Polygon(
    (
        (845200, 6525200),
        (845300, 6525200),
        (845300, 6525300),
        (845200, 6525300),
        (845200, 6525200),
    ),
    srid=2154,
)


@override_settings(CACHES=NO_CACHE)
class DashboardViewMultiCityTest(TestCase):
    """Tests for metropole-level aggregation with multiple cities."""

    @classmethod
    def setUpTestData(cls):
        cls.city_a = CityFactory(
            code="69123",
            name="Lyon",
            geometry=GEOM,
            plantability_counts={"0": 10, "5": 20, "10": 30},
        )
        cls.city_b = CityFactory(
            code="69266",
            name="Villeurbanne",
            geometry=GEOM_B,
            plantability_counts={"0": 5, "5": 15, "10": 25},
        )

    def setUp(self):
        self.client = Client()
        self.url = reverse("dashboard")

    def test_metropole_aggregates_counts_across_cities(self):
        """Total counts: 0→15, 5→35, 10→55. Avg = (0*15+5*35+10*55)/105 = 725/105 ≈ 6.9."""
        data = self.client.get(self.url).json()
        self.assertAlmostEqual(
            data["plantability"]["averageNormalizedIndice"], 6.9, places=1
        )

    def test_metropole_lists_both_city_divisions(self):
        data = self.client.get(self.url).json()
        divisions = data["plantability"]["distributionByDivision"]
        codes = {d["code"] for d in divisions}
        self.assertEqual(codes, {"69123", "69266"})

    def test_metropole_area_sums_both_cities(self):
        data = self.client.get(self.url).json()
        self.assertGreater(data["areaHa"], 0)


@override_settings(CACHES=NO_CACHE)
class DashboardViewIrisCodePriorityTest(TestCase):
    """Tests that iris_code takes priority when both params are provided."""

    @classmethod
    def setUpTestData(cls):
        cls.city = CityFactory(
            code="69123",
            name="Lyon",
            geometry=GEOM,
            plantability_counts={"0": 100, "10": 100},
        )
        cls.iris = IrisFactory(
            code="691230101",
            name="Presqu'ile",
            city=cls.city,
            geometry=GEOM,
            plantability_counts={"0": 10, "10": 10},
        )

    def setUp(self):
        self.client = Client()
        self.url = reverse("dashboard")

    def test_iris_code_takes_priority_over_city_code(self):
        """When both params are provided, iris_code should be used."""
        data = self.client.get(
            self.url, {"city_code": "69123", "iris_code": "691230101"}
        ).json()
        divisions = data["plantability"]["distributionByDivision"]
        self.assertEqual(divisions, [])


@override_settings(CACHES=NO_CACHE)
class DashboardViewNaturalLczOnlyTest(TestCase):
    """Tests that building metrics are zero when only natural LCZ exist."""

    @classmethod
    def setUpTestData(cls):
        cls.city = CityFactory(code="69123", name="Lyon", geometry=GEOM)

        LczFactory(
            geometry=GEOM,
            lcz_index="A",
            details={
                "hre": 0.0,
                "bur": 0.0,
                "ror": 5.0,
                "bsr": 10.0,
                "ver": 80.0,
                "war": 5.0,
                "vhr": 60.0,
            },
        )
        LczFactory(
            geometry=GEOM,
            lcz_index="D",
            details={
                "hre": 0.0,
                "bur": 0.0,
                "ror": 10.0,
                "bsr": 20.0,
                "ver": 60.0,
                "war": 10.0,
                "vhr": 30.0,
            },
        )

    def setUp(self):
        self.client = Client()
        self.url = reverse("dashboard")

    def test_built_only_metrics_are_zero_with_natural_lcz(self):
        data = self.client.get(self.url, {"city_code": "69123"}).json()
        lcz = data["lcz"]

        self.assertEqual(lcz["averageBuildingSurfaceRate"], 0)
        self.assertEqual(lcz["averageBuildingHeight"], 0)

    def test_surface_metrics_still_computed_with_natural_lcz(self):
        data = self.client.get(self.url, {"city_code": "69123"}).json()
        lcz = data["lcz"]

        self.assertEqual(lcz["totalVegetationRate"], 70.0)
        self.assertGreater(lcz["treeCoverRate"], 0)


@override_settings(CACHES=NO_CACHE)
class DashboardViewDivisionNameFallbackTest(TestCase):
    """Tests that division name falls back to code when name is empty."""

    @classmethod
    def setUpTestData(cls):
        cls.city = CityFactory(
            code="69123",
            name="Lyon",
            geometry=GEOM,
        )
        cls.iris_no_name = IrisFactory(
            code="691230102",
            name="",
            city=cls.city,
            geometry=GEOM,
            plantability_counts={"5": 10},
        )

    def setUp(self):
        self.client = Client()
        self.url = reverse("dashboard")

    def test_division_name_falls_back_to_code(self):
        data = self.client.get(self.url, {"city_code": "69123"}).json()
        divisions = data["plantability"]["distributionByDivision"]

        names = {d["code"]: d["name"] for d in divisions}
        self.assertEqual(names["691230102"], "691230102")


@override_settings(CACHES=NO_CACHE)
class DashboardViewCityLczValuesTest(TestCase):
    """Tests that city-level LCZ and vulnerability values are correct."""

    @classmethod
    def setUpTestData(cls):
        cls.city = CityFactory(code="69123", name="Lyon", geometry=GEOM)

        LczFactory(
            geometry=GEOM,
            lcz_index="5",
            details={
                "hre": 20.0,
                "bur": 40.0,
                "ror": 20.0,
                "bsr": 5.0,
                "ver": 30.0,
                "war": 5.0,
                "vhr": 15.0,
            },
        )

        VulnerabilityFactory(
            geometry=GEOM,
            vulnerability_index_day=7.0,
            vulnerability_index_night=5.0,
            expo_index_day=3.0,
            expo_index_night=2.0,
            sensibilty_index_day=2.0,
            sensibilty_index_night=1.5,
            capaf_index_day=2.0,
            capaf_index_night=1.5,
        )

    def setUp(self):
        self.client = Client()
        self.url = reverse("dashboard")

    def test_city_lcz_values(self):
        data = self.client.get(self.url, {"city_code": "69123"}).json()
        lcz = data["lcz"]

        self.assertEqual(lcz["averageBuildingHeight"], 20.0)
        self.assertEqual(lcz["averageBuildingSurfaceRate"], 40.0)
        self.assertEqual(lcz["impermeableSurfaceRate"], 20.0)
        self.assertEqual(lcz["totalVegetationRate"], 30.0)

    def test_city_vulnerability_values(self):
        data = self.client.get(self.url, {"city_code": "69123"}).json()
        vuln = data["vulnerability"]

        self.assertEqual(vuln["averageDay"], 7.0)
        self.assertEqual(vuln["averageNight"], 5.0)
        self.assertEqual(vuln["expoDay"], 3.0)
        self.assertEqual(vuln["expoNight"], 2.0)


@override_settings(CACHES=NO_CACHE)
class DashboardViewIrisPlantabilityTest(TestCase):
    """Tests that iris-level plantability uses iris.plantability_counts."""

    @classmethod
    def setUpTestData(cls):
        cls.city = CityFactory(code="69123", name="Lyon", geometry=GEOM)
        cls.iris = IrisFactory(
            code="691230101",
            name="Presqu'ile",
            city=cls.city,
            geometry=GEOM,
            plantability_counts={"2": 10, "8": 10},
        )

    def setUp(self):
        self.client = Client()
        self.url = reverse("dashboard")

    def test_iris_plantability_average(self):
        """(2*10 + 8*10) / 20 = 100/20 = 5.0."""
        data = self.client.get(self.url, {"iris_code": "691230101"}).json()
        self.assertEqual(data["plantability"]["averageNormalizedIndice"], 5.0)

    def test_iris_plantability_distribution(self):
        data = self.client.get(self.url, {"iris_code": "691230101"}).json()
        dist = data["plantability"]["distribution"]
        self.assertEqual(dist["2"], 10)
        self.assertEqual(dist["8"], 10)


@override_settings(CACHES=NO_CACHE)
class DashboardViewAreaHaTest(TestCase):
    """Tests that areaHa is correctly computed at each scale."""

    @classmethod
    def setUpTestData(cls):
        cls.city = CityFactory(code="69123", name="Lyon", geometry=GEOM)
        cls.iris = IrisFactory(
            code="691230101", name="Presqu'ile", city=cls.city, geometry=GEOM
        )

    def setUp(self):
        self.client = Client()
        self.url = reverse("dashboard")

    def test_city_area_ha(self):
        data = self.client.get(self.url, {"city_code": "69123"}).json()
        self.assertGreater(data["areaHa"], 0)

    def test_iris_area_ha(self):
        data = self.client.get(self.url, {"iris_code": "691230101"}).json()
        self.assertGreater(data["areaHa"], 0)

    def test_metropole_area_ha(self):
        data = self.client.get(self.url).json()
        self.assertGreater(data["areaHa"], 0)
