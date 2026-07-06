import json
import logging

import numpy as np
from shapely.geometry.polygon import Polygon as ShapelyPolygon

from django.contrib.gis.geos import Polygon
from django.core.management import call_command
from django.db.models import Avg
from django.test import SimpleTestCase, TestCase, Client, override_settings
from django.urls import reverse

from api.views.dashboard_views import _avg_from_counts, _safe_round
from iarbre_data.management.commands.populate import CITY_CODE
from iarbre_data.management.commands.populate import Command as PopulateCommand
from iarbre_data.models import City, Iris, Tile, Vulnerability
from iarbre_data.settings import SRID_DB
from iarbre_data.utils.database import select_city
from iarbre_data.utils.utils_populate import HexTileShape, create_tiles_for_city
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
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Build the city and its tiles the same way populate() does, but skip
        # its IRIS step (a live fetch from an external API not available in tests).
        (x, y) = PopulateCommand.city_center
        radius = 2500
        city_geometry = ShapelyPolygon(
            (
                (x - radius, y - radius),
                (x + radius, y - radius),
                (x + radius, y + radius),
                (x - radius, y + radius),
                (x - radius, y - radius),
            )
        )
        cls.city = City.objects.create(
            name="Villard-de-Lans", code=CITY_CODE, geometry=city_geometry.wkt
        )
        # Iris must exist before tile creation: create_tiles_for_city() looks up
        # intersecting Iris to set each tile's iris_id at creation time.
        cls.iris = IrisFactory(city=cls.city, geometry=cls.city.geometry)
        create_tiles_for_city(
            city=select_city(CITY_CODE).iloc[0],
            grid_size=50,
            tile_shape_cls=HexTileShape,
            logger=logging.getLogger(__name__),
            batch_size=int(1e6),
            side_length=50,
            height_ratio=np.sin(np.pi / 3),
        )

        populate_cmd = PopulateCommand()
        populate_cmd.city = cls.city
        populate_cmd._generate_plantability_tiles()
        populate_cmd.generate_vulnerability_zones()
        call_command("compute_plantability_counts")

        # populate() has no equivalent for these layers, so add minimal data on the real city footprint.
        LczFactory(
            geometry=cls.city.geometry,
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
            geometry=cls.city.geometry, strate="arborescent", surface=500_000
        )
        VegestrateFactory(
            geometry=cls.city.geometry, strate="arbustif", surface=200_000
        )
        VegestrateFactory(
            geometry=cls.city.geometry, strate="herbacee", surface=300_000
        )
        DataFactory(geometry=cls.city.geometry, factor="Bâtiments")
        BiosphereFunctionalIntegrityFactory(geometry=cls.city.geometry, indice=70)

        cls.city.refresh_from_db()
        cls.iris.refresh_from_db()

    def setUp(self):
        self.client = Client()
        self.url = reverse("dashboard")

    def test_metropole_returns_structure(self):
        data = self.client.get(self.url).json()
        self.assertIsNone(data["city"])
        for key in [
            "areaKm2",
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
        expected = _safe_round(_avg_from_counts(self.city.plantability_counts))
        self.assertEqual(plantability["averageNormalizedIndice"], expected)
        divisions = plantability["distributionByDivision"]
        self.assertEqual(len(divisions), City.objects.count())
        self.assertEqual(divisions[0]["code"], self.city.code)

    def test_city_filter(self):
        data = self.client.get(self.url, {"city_code": CITY_CODE}).json()
        self.assertEqual(data["city"]["code"], CITY_CODE)
        self.assertEqual(data["city"]["name"], self.city.name)
        divisions = data["plantability"]["distributionByDivision"]
        self.assertEqual(len(divisions), Iris.objects.filter(city=self.city).count())
        self.assertEqual(divisions[0]["code"], self.iris.code)

    def test_iris_filter(self):
        data = self.client.get(self.url, {"iris_code": self.iris.code}).json()
        self.assertEqual(data["city"]["code"], CITY_CODE)
        self.assertEqual(data["plantability"]["distributionByDivision"], [])
        expected = _safe_round(_avg_from_counts(self.iris.plantability_counts))
        self.assertAlmostEqual(
            data["plantability"]["averageNormalizedIndice"], expected
        )

    def test_iris_code_priority_over_city_code(self):
        data = self.client.get(
            self.url, {"city_code": CITY_CODE, "iris_code": self.iris.code}
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
        expected = Vulnerability.objects.aggregate(
            avg_day=Avg("vulnerability_index_day"),
            avg_night=Avg("vulnerability_index_night"),
            avg_expo_day=Avg("expo_index_day"),
            avg_expo_night=Avg("expo_index_night"),
        )
        self.assertEqual(vuln["averageDay"], _safe_round(expected["avg_day"]))
        self.assertEqual(vuln["averageNight"], _safe_round(expected["avg_night"]))
        self.assertEqual(vuln["expoDay"], _safe_round(expected["avg_expo_day"]))
        self.assertEqual(vuln["expoNight"], _safe_round(expected["avg_expo_night"]))

    def test_vegetation_values(self):
        data = self.client.get(self.url).json()
        veg = data["vegetation"]
        self.assertEqual(veg["totalM2"], 1_000_000.0)
        self.assertEqual(veg["treesSurfaceM2"], 500_000.0)
        self.assertEqual(veg["bushesSurfaceM2"], 200_000.0)
        self.assertEqual(veg["grassSurfaceM2"], 300_000.0)

    def test_lcz_values(self):
        data = self.client.get(self.url).json()
        lcz = data["lcz"]
        self.assertEqual(lcz["averageBuildingSurfaceRate"], 20.0)
        self.assertEqual(lcz["averageBuildingHeight"], 15.0)
        self.assertEqual(lcz["impermeableSurfaceRate"], 30.0)
        self.assertEqual(lcz["totalVegetationRate"], 40.0)

    def test_biosphere_values(self):
        data = self.client.get(self.url).json()
        biosphere = data["biosphere"]
        self.assertEqual(biosphere["averageIndice"], 70.0)
        self.assertEqual(biosphere["distribution"], {"70": 1})

    def test_buildings_value(self):
        data = self.client.get(self.url).json()
        expected = _safe_round(self.city.geometry.area)
        self.assertEqual(data["buildings"]["averageBuildingFootprintM2"], expected)


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
        self.assertEqual(data["vegetation"]["totalM2"], 0)
        self.assertEqual(data["buildings"]["averageBuildingFootprintM2"], 0)
        self.assertEqual(data["biosphere"]["averageIndice"], 0)


@override_settings(CACHES=NO_CACHE)
class DashboardMetaFactorsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("dashboard")
        self.city = CityFactory(
            code="38250",
            name="Villard-de-Lans",
            geometry=VILLARD_SQUARE,
            plantability_counts={"0": 0, "2": 0, "4": 0, "6": 0, "8": 0, "10": 10},
            meta_factors_avg={"eau": 0.4, "bati": 0.3},
        )

    def test_city_meta_factors_returned(self):
        data = self.client.get(self.url, {"city_code": "38250"}).json()
        self.assertEqual(data["plantability"]["metaFactors"], {"eau": 0.4, "bati": 0.3})

    def test_metropole_averages_meta_factors_across_cities(self):
        CityFactory(
            code="69001",
            geometry=VILLARD_SQUARE,
            plantability_counts={"0": 0, "2": 0, "4": 0, "6": 0, "8": 0, "10": 10},
            meta_factors_avg={"eau": 0.8, "bati": 0.1},
        )
        data = self.client.get(self.url).json()
        mf = data["plantability"]["metaFactors"]
        self.assertAlmostEqual(mf["eau"], 0.6, places=1)
        self.assertAlmostEqual(mf["bati"], 0.2, places=1)

    def test_metropole_skips_cities_without_meta_factors(self):
        CityFactory(
            code="69001",
            geometry=VILLARD_SQUARE,
            plantability_counts={"0": 0, "2": 0, "4": 0, "6": 0, "8": 0, "10": 10},
            meta_factors_avg=None,
        )
        data = self.client.get(self.url).json()
        self.assertEqual(data["plantability"]["metaFactors"], {"eau": 0.4, "bati": 0.3})


LYON_SQUARE = Polygon(
    (
        (845000, 6525000),
        (845100, 6525000),
        (845100, 6525100),
        (845000, 6525100),
        (845000, 6525000),
    ),
    srid=SRID_DB,
)

# WGS84 polygon that transforms into LYON_SQUARE's area (mirrors in-polygon tests).
LYON_WGS84_POLYGON = {
    "type": "Polygon",
    "coordinates": [
        [
            [4.867256, 45.809200],
            [4.868544, 45.809179],
            [4.868574, 45.810079],
            [4.867287, 45.810101],
            [4.867256, 45.809200],
        ]
    ],
}


@override_settings(CACHES=NO_CACHE)
class DashboardPolygonViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("dashboard-in-polygon")
        self.iris = IrisFactory(
            code="690010101",
            city=CityFactory(code="69001", geometry=LYON_SQUARE),
            geometry=LYON_SQUARE,
            meta_factors_avg={"eau": 0.4, "bati": 0.2},
        )
        Tile.objects.create(
            geometry=LYON_SQUARE,
            plantability_normalized_indice=8.0,
            iris=self.iris,
            city=self.iris.city,
        )
        VulnerabilityFactory(
            geometry=LYON_SQUARE,
            vulnerability_index_day=6.0,
            vulnerability_index_night=4.0,
        )
        LczFactory(
            geometry=LYON_SQUARE,
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
        VegestrateFactory(geometry=LYON_SQUARE, strate="arborescent", surface=500_000)

    def _post(self, payload):
        return self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )

    def test_returns_full_structure(self):
        data = self._post(LYON_WGS84_POLYGON).json()
        for key in [
            "areaKm2",
            "plantability",
            "vulnerability",
            "vegetation",
            "lcz",
            "biosphere",
            "buildings",
        ]:
            self.assertIn(key, data)
        self.assertIsNone(data["city"])

    def test_plantability_from_tiles(self):
        plantability = self._post(LYON_WGS84_POLYGON).json()["plantability"]
        self.assertAlmostEqual(plantability["averageNormalizedIndice"], 8.0, places=1)
        self.assertEqual(plantability["distribution"], {"8": 1})
        self.assertEqual(plantability["distributionByDivision"], [])

    def test_meta_factors_weighted_from_iris(self):
        plantability = self._post(LYON_WGS84_POLYGON).json()["plantability"]
        self.assertEqual(plantability["metaFactors"], {"eau": 0.4, "bati": 0.2})

    def test_vulnerability_aggregated(self):
        vuln = self._post(LYON_WGS84_POLYGON).json()["vulnerability"]
        self.assertEqual(vuln["averageDay"], 6.0)
        self.assertEqual(vuln["averageNight"], 4.0)

    def test_empty_polygon_returns_zeros(self):
        far_away = {
            "type": "Polygon",
            "coordinates": [
                [[2.0, 48.0], [2.01, 48.0], [2.01, 48.01], [2.0, 48.01], [2.0, 48.0]]
            ],
        }
        data = self._post(far_away).json()
        self.assertEqual(data["plantability"]["averageNormalizedIndice"], 0)
        self.assertEqual(data["plantability"]["metaFactors"], {})
        self.assertEqual(data["vulnerability"]["averageDay"], 0)

    def test_oversized_polygon_rejected(self):
        oversized = {
            "type": "Polygon",
            "coordinates": [
                [[4.0, 45.0], [6.0, 45.0], [6.0, 46.0], [4.0, 46.0], [4.0, 45.0]]
            ],
        }
        self.assertEqual(self._post(oversized).status_code, 400)

    def test_empty_payload_rejected(self):
        response = self.client.post(self.url, data="", content_type="application/json")
        self.assertEqual(response.status_code, 400)


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
