from django.test import TestCase, Client
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
            mvt_file=b"test_mvt_data",
        )

    def test_valid_tile_retrieval(self):
        url = "/api/tiles/city/test/10/512/256/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "application/x-protobuf")
        self.assertEqual(response.content, b"test_mvt_data")

    def test_nonexistent_tile_returns_404(self):
        url = "/api/tiles/city/test/10/999/999/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class TileDetailsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.lcz = Lcz.objects.create(id=1)
        self.vulnerability = Vulnerability.objects.create(id=2)
        self.tile = Tile.objects.create(id=3)

    def test_lcz_details_retrieval(self):
        url = "/api/tile-details/lcz/1/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response["content-type"])

    def test_vulnerability_details_retrieval(self):
        url = "/api/tile-details/vulnerability/2/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response["content-type"])

    def test_plantability_details_retrieval(self):
        url = "/api/tile-details/plantability/3/"
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

            url = f"/api/tile-details/{datatype}/{obj_id}/"
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
