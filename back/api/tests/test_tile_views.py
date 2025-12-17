import json
from django.test import TestCase, Client
from django.core.files.base import ContentFile
from django.contrib.gis.geos import Polygon
from iarbre_data.models import MVTTile, Tile, Lcz, Vulnerability


class TileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.mvt_tile = MVTTile.objects.create(
            geolevel="city",
            datatype="test",
            zoom_level=10,
            tile_x=512,
            tile_y=256,
            mvt_file=ContentFile(b"test_mvt_data", name="test.mvt"),
        )

    def test_valid_tile_retrieval(self):
        url = "/api/tiles/city/test/10/512/256.mvt"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "application/x-protobuf")
        self.assertTrue(len(response.content) > 0)  # Has content

    def test_nonexistent_tile_returns_404(self):
        url = "/api/tiles/city/test/10/999/999.mvt"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class TileDetailsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create 1m x 1m square polygon
        square = Polygon(((0, 0), (1, 0), (1, 1), (0, 1), (0, 0)), srid=2154)
        self.lcz = Lcz.objects.create(id=1, geometry=square)
        self.vulnerability = Vulnerability.objects.create(id=2, geometry=square)
        self.tile = Tile.objects.create(id=3, geometry=square)

    def test_lcz_details_retrieval(self):
        url = "/api/tiles/lcz/1/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response["content-type"])

    def test_vulnerability_details_retrieval(self):
        url = "/api/tiles/vulnerability/2/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response["content-type"])

    def test_plantability_details_retrieval(self):
        url = "/api/tiles/plantability/3/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response["content-type"])

    def test_valid_datatypes_supported(self):
        valid_datatypes = ["lcz", "vulnerability", "plantability"]

        for datatype in valid_datatypes:
            if datatype == "lcz":
                obj_id = self.lcz.id
            elif datatype == "vulnerability":
                obj_id = self.vulnerability.id
            else:
                obj_id = self.tile.id

            url = f"/api/tiles/{datatype}/{obj_id}/"
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_plantability_details_with_json_string(self):
        # Create tile with JSON string details
        square = Polygon(((0, 0), (1, 0), (1, 1), (0, 1), (0, 0)), srid=2154)
        tile_with_json = Tile.objects.create(
            geometry=square, details='{"plantabilityNormalizedIndice": 5, "id": 42}'
        )

        url = f"/api/tiles/plantability/{tile_with_json.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(
            response_data["details"], {"plantabilityNormalizedIndice": 5, "id": 42}
        )

    def test_plantability_details_with_invalid_json_string(self):
        square = Polygon(((0, 0), (1, 0), (1, 1), (0, 1), (0, 0)), srid=2154)
        tile_with_invalid_json = Tile.objects.create(
            geometry=square, details="invalid json string"
        )

        url = f"/api/tiles/plantability/{tile_with_invalid_json.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIsNone(response_data["details"])


class ScoresInPolygonViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        lyon_square = Polygon(
            (
                (845000, 6525000),
                (845100, 6525000),
                (845100, 6525100),
                (845000, 6525100),
                (845000, 6525000),
            ),
            srid=2154,
        )
        self.tile = Tile.objects.create(
            geometry=lyon_square, plantability_normalized_indice=7.5
        )
        self.vulnerability = Vulnerability.objects.create(
            geometry=lyon_square,
            vulnerability_index_day=5.0,
            vulnerability_index_night=4.0,
        )

    def test_valid_plantability_polygon(self):
        url = "/api/tiles/plantability/in-polygon/"
        polygon = {
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
        response = self.client.post(
            url, data=json.dumps(polygon), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["datatype"], "plantability")
        self.assertIn("count", data)
        self.assertIn("plantabilityNormalizedIndice", data)

    def test_valid_vulnerability_polygon(self):
        url = "/api/tiles/vulnerability/in-polygon/"
        polygon = {
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
        response = self.client.post(
            url, data=json.dumps(polygon), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["datatype"], "vulnerability")
        self.assertIn("vulnerabilityIndiceDay", data)

    def test_invalid_datatype(self):
        url = "/api/tiles/invalid/in-polygon/"
        polygon = {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]}
        response = self.client.post(
            url, data=json.dumps(polygon), content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

    def test_empty_polygon_data(self):
        url = "/api/tiles/plantability/in-polygon/"
        response = self.client.post(url, data="", content_type="application/json")

        self.assertEqual(response.status_code, 400)

    def test_no_tiles_found(self):
        url = "/api/tiles/plantability/in-polygon/"
        polygon = {
            "type": "Polygon",
            "coordinates": [
                [
                    [2.0, 48.0],
                    [2.01, 48.0],
                    [2.01, 48.01],
                    [2.0, 48.01],
                    [2.0, 48.0],
                ]
            ],
        }
        response = self.client.post(
            url, data=json.dumps(polygon), content_type="application/json"
        )

        self.assertEqual(response.status_code, 404)
