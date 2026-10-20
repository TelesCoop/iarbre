from unittest.mock import MagicMock, patch

from django.contrib.gis.geos import Polygon
from django.test import TestCase

from iarbre_data.factories import CityFactory
from iarbre_data.management.commands.c01_insert_cities_and_iris import Command
from iarbre_data.models import City, Iris
from iarbre_data.settings import SRID_DB

BELLECOUR = {
    "type": "Feature",
    "geometry": {
        "type": "MultiPolygon",
        "coordinates": [
            [
                [
                    [842000, 6518500],
                    [842500, 6518500],
                    [842500, 6519000],
                    [842000, 6519000],
                    [842000, 6518500],
                ]
            ]
        ],
    },
    "properties": {
        "code_insee": "69382",
        "code_iris": "693820202",
        "nom_iris": "Bellecour-A Gourjus",
    },
}


def ign_response(params, **kwargs):
    response = MagicMock()
    features = [BELLECOUR] if params["CQL_FILTER"] == "code_insee='69382'" else []
    response.json.return_value = {"type": "FeatureCollection", "features": features}
    return response


class InsertIrisCommandTest(TestCase):
    @patch(
        "iarbre_data.management.commands.c01_insert_cities_and_iris.requests.get",
        side_effect=lambda url, params, **kwargs: ign_response(params),
    )
    def test_insert_iris_attaches_each_iris_to_the_city_of_its_code(self, _):
        CityFactory(
            code="69382",
            name="Lyon 2e Arrondissement",
            geometry=Polygon.from_bbox((841500, 6516000, 843000, 6519000)),
        )
        CityFactory(
            code="69385",
            name="Lyon 5e Arrondissement",
            geometry=Polygon.from_bbox((840000, 6518500, 842000, 6520000)),
        )

        Command._insert_iris(City.objects.all())

        iris = Iris.objects.get()
        self.assertEqual(iris.code, "693820202")
        self.assertEqual(iris.city.code, "69382")
        self.assertEqual(iris.geometry.geom_type, "Polygon")
        self.assertEqual(iris.geometry.srid, SRID_DB)
