import time
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, CommandError

from iarbre_data.utils.hourly_rasters import split_hours

HOURLY_RASTERS = ["PET_index_1m_2090", "PET_index_2020", "Shadow"]


class Command(BaseCommand):
    help = (
        "Split the multi-band hourly WMS rasters (band = hour + 1) into one "
        "single-band GeoTIFF per hour: rasters/WMS/<name>/<name>_hXX.tif."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "names",
            nargs="*",
            default=HOURLY_RASTERS,
            help=f"Rasters of rasters/WMS, without .tif (default: {HOURLY_RASTERS}).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Regenerate hour files even if they are up to date.",
        )

    def handle(self, *args, **options):
        wms_dir = Path(settings.MEDIA_ROOT) / "rasters/WMS"
        sources = [wms_dir / f"{name}.tif" for name in options["names"]]
        missing = [path.name for path in sources if not path.exists()]
        if missing:
            raise CommandError(f"Missing rasters in {wms_dir}: {', '.join(missing)}")

        for src_path in sources:
            self.stdout.write(src_path.name)
            start = time.monotonic()
            for dst_path, built in split_hours(src_path, force=options["force"]):
                if built:
                    elapsed = time.monotonic() - start
                    self.stdout.write(
                        self.style.SUCCESS(f"  {dst_path.name} built ({elapsed:.1f}s)")
                    )
                    start = time.monotonic()
                else:
                    self.stdout.write(f"  {dst_path.name} skipped")
