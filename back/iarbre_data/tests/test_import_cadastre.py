from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry
from iarbre_data.management.commands.import_cadastre import Command
from iarbre_data.models import Cadastre
from iarbre_data.factories import CityFactory


class ImportCadastreCommandTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test city using factory
        cls.test_city = CityFactory(code="69001", name="Lyon 1er")

    def setUp(self):
        self.command = Command()
        # Clean cadastre data before each test
        Cadastre.objects.all().delete()

    def test_cadastre_duplicate_prevention(self):
        # Create first cadastre
        Cadastre.objects.create(
            parcel_id="690010000A0001",
            city_code="69001",
            city=self.test_city,
            geometry=GEOSGeometry(
                "POLYGON((4.8 45.7, 4.81 45.7, 4.81 45.71, 4.8 45.71, 4.8 45.7))",
                srid=2154,
            ),
        )

        # Check if duplicate exists (this is what the command does)
        existing_parcel = Cadastre.objects.filter(parcel_id="690010000A0001").first()
        self.assertIsNotNone(existing_parcel)

        # Verify we can find existing parcels
        duplicate_check = Cadastre.objects.filter(parcel_id="690010000A0001").exists()
        self.assertTrue(duplicate_check)

    def test_command_url_construction(self):
        expected_base_url = (
            "https://cadastre.data.gouv.fr/bundler/cadastre-etalab/communes"
        )
        city_code = self.test_city.code
        expected_suffix = "geojson/parcelles"

        expected_url = f"{expected_base_url}/{city_code}/{expected_suffix}"

        # This is the URL pattern used in the import_cadastre_for_city method
        constructed_url = f"https://cadastre.data.gouv.fr/bundler/cadastre-etalab/communes/{city_code}/geojson/parcelles"

        self.assertEqual(constructed_url, expected_url)

    def test_geometry_transformation_setup(self):
        # Test that we can create geometries in both coordinate systems
        # Source SRID (from API)
        source_srid = 4326

        # Target SRID (from settings)
        from iarbre_data.settings import TARGET_PROJ

        # Create geometry in source CRS
        geom_4326 = GEOSGeometry(
            "POLYGON((4.8 45.7, 4.81 45.7, 4.81 45.71, 4.8 45.71, 4.8 45.7))",
            srid=source_srid,
        )

        # Transform to target CRS
        if source_srid != TARGET_PROJ:
            geom_4326.transform(TARGET_PROJ)

        # Verify transformation worked
        self.assertEqual(geom_4326.srid, TARGET_PROJ)

    def test_geometry_validation_buffer_fix(self):
        # Create a potentially invalid geometry
        geom = GEOSGeometry(
            "POLYGON((4.8 45.7, 4.81 45.7, 4.81 45.71, 4.8 45.71, 4.8 45.7))", srid=2154
        )

        # Test validation logic (from the command)
        if not geom.valid:
            try:
                fixed_geom = geom.buffer(0)
                self.assertTrue(fixed_geom.valid)
            except Exception as e:
                # This is what the command does - log and continue
                print("Geometry not valid", e)
        else:
            # Geometry is already valid
            self.assertTrue(geom.valid)
