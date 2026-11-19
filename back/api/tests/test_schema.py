"""OpenAPI schema of the public API (drf-spectacular)."""

from django.test import SimpleTestCase
from django.urls import reverse
from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.validation import validate_schema


class PublicSchemaTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.schema = SchemaGenerator().get_schema(request=None, public=True)

    def test_schema_is_valid_openapi(self):
        validate_schema(self.schema)

    def test_only_public_routes_are_documented(self):
        paths = self.schema["paths"]
        self.assertTrue(paths)
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue(path.startswith("/api/v1/"))

    def test_public_routes_are_documented(self):
        for path in [
            "/api/v1/cities/",
            "/api/v1/dashboard/",
            "/api/v1/dashboard/in-polygon/",
            "/api/v1/tiles/{datatype}/in-polygon/",
            "/api/v1/wms/",
            "/api/v1/rasters/{raster_type}/",
            "/api/v1/metadata/",
        ]:
            with self.subTest(path=path):
                self.assertIn(path, self.schema["paths"])

    def test_response_keys_are_camel_case(self):
        properties = self.schema["components"]["schemas"]["Metadata"]["properties"]
        self.assertEqual(list(properties), ["generationDate"])


class SchemaViewsTest(SimpleTestCase):
    def test_schema_endpoint(self):
        response = self.client.get(reverse("schema"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"openapi:", response.content)

    def test_swagger_ui(self):
        response = self.client.get(reverse("swagger-ui"))
        self.assertEqual(response.status_code, 200)
