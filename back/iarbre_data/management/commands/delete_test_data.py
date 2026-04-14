from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand
from django.db import transaction

from iarbre_data.management.commands.populate import CITY_CODE
from iarbre_data.models import City, Data, Lcz, MVTTile, Vulnerability


class Command(BaseCommand):
    help = (
        "Delete all test data created by the populate command "
        "(Villard-de-Lans city and all geographically related data)."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            city = City.objects.get(code=CITY_CODE)
        except City.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"No test city with code {CITY_CODE}"))
            return

        city_geometry = GEOSGeometry(city.geometry.wkt)

        lcz_deleted, _ = Lcz.objects.filter(geometry__intersects=city_geometry).delete()
        vuln_deleted, _ = Vulnerability.objects.filter(
            geometry__intersects=city_geometry
        ).delete()
        qpv_deleted, _ = Data.objects.filter(
            geometry__intersects=city_geometry, factor="QPV"
        ).delete()

        # MVTTiles are not geographically scoped, so wipe them all to ensure
        # tiles generated for test data do not leak to production
        mvt_deleted, _ = MVTTile.objects.all().delete()

        # Cascade deletes Iris, Tile, and any FK-linked records
        city.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted test data: city {CITY_CODE}, "
                f"{lcz_deleted} LCZ, {vuln_deleted} vulnerabilities, "
                f"{qpv_deleted} QPV, {mvt_deleted} MVT tiles"
            )
        )
