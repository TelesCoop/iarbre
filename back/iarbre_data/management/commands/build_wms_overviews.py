import time
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand

from iarbre_data.utils.raster_overviews import build_overviews


class Command(BaseCommand):
    help = "Build external overviews (.tif.ovr) for the WMS rasters."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Rebuild overviews even if they are up to date.",
        )

    def handle(self, *args, **options):
        wms_dir = Path(settings.MEDIA_ROOT) / "rasters/WMS"
        for path in sorted(wms_dir.glob("*.tif")):
            start = time.monotonic()
            if build_overviews(path, force=options["force"]):
                elapsed = time.monotonic() - start
                self.stdout.write(
                    self.style.SUCCESS(f"  {path.name} built in {elapsed:.1f}s")
                )
            else:
                self.stdout.write(f"  {path.name} skipped")
