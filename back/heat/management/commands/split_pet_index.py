from pathlib import Path

import rasterio
from django.conf import settings
from django.core.management import BaseCommand

from heat.raster import extract_band, hour_raster_path, is_up_to_date


class Command(BaseCommand):
    help = (
        "Split the multi-band PET index GeoTIFF into one single-band GeoTIFF per hour."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            type=str,
            default=str(Path(settings.MEDIA_ROOT) / "rasters/WMS/PET_index.tif"),
            help="Multi-band GeoTIFF, band = hour + 1",
        )
        parser.add_argument(
            "--force", action="store_true", help="Regenerate up-to-date hour files"
        )

    def handle(self, *args, **options):
        src_path = Path(options["source"])
        with rasterio.open(src_path) as src:
            band_count = src.count

        for hour in range(band_count):
            dst_path = hour_raster_path(src_path, hour)
            if not options["force"] and is_up_to_date(src_path, dst_path):
                self.stdout.write(f"Hour {hour:02d}: up to date, skipped")
                continue
            extract_band(src_path, hour + 1, dst_path)
            self.stdout.write(self.style.SUCCESS(f"Hour {hour:02d}: {dst_path}"))
