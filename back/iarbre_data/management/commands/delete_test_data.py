import mercantile
from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from iarbre_data.management.commands.populate import CITY_CODE
from iarbre_data.models import City, Data, Lcz, MVTTile, Vulnerability
from iarbre_data.settings import SRID_DOWNLOADED_DATA


class Command(BaseCommand):
    help = (
        "Delete all test data created by the populate command "
        "(Villard-de-Lans city and all geographically related data, "
        "including the MVT tiles intersecting the test city bounding box)."
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

        mvt_deleted = self._delete_mvt_tiles_for_geometry(city_geometry)

        # Cascade deletes Iris, Tile, and any FK-linked records
        city.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted test data: city {CITY_CODE}, "
                f"{lcz_deleted} LCZ, {vuln_deleted} vulnerabilities, "
                f"{qpv_deleted} QPV, {mvt_deleted} MVT tiles"
            )
        )

    def _delete_mvt_tiles_for_geometry(self, city_geometry):
        """Delete only the MVT tiles whose XYZ coordinates intersect the city bbox."""
        wgs84_geometry = city_geometry.clone()
        if wgs84_geometry.srid != SRID_DOWNLOADED_DATA:
            wgs84_geometry.transform(SRID_DOWNLOADED_DATA)
        west, south, east, north = wgs84_geometry.extent

        zoom_levels = MVTTile.objects.values_list("zoom_level", flat=True).distinct()
        tile_filters = Q()
        for zoom in zoom_levels:
            tiles = mercantile.tiles(west, south, east, north, zoom)
            xy_pairs = {(tile.x, tile.y) for tile in tiles}
            for tile_x, tile_y in xy_pairs:
                tile_filters |= Q(zoom_level=zoom, tile_x=tile_x, tile_y=tile_y)

        if not tile_filters:
            return 0

        deleted, _ = MVTTile.objects.filter(tile_filters).delete()
        return deleted
