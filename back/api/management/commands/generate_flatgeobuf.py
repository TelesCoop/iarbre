"""Export plantability and vegestrate vector data to FlatGeobuf files.

Uses ogr2ogr to stream directly from PostGIS to FlatGeobuf without loading
the entire dataset into memory — critical for the ~21M plantability tiles.

The generated .fgb files include a packed Hilbert R-tree spatial index,
enabling QGIS to stream only the features within the current viewport
via HTTP range requests.

Usage:
    python manage.py generate_flatgeobuf
    python manage.py generate_flatgeobuf --dataset plantability
    python manage.py generate_flatgeobuf --dataset vegestrate
"""

import os
import subprocess
import time

from django.conf import settings
from django.core.management import BaseCommand

from iarbre_data.utils.database import log_progress

DATASETS = {
    "plantability": {
        "sql": (
            "SELECT id, geometry, plantability_indice, plantability_normalized_indice"
            " FROM iarbre_data_tile"
            " WHERE plantability_normalized_indice IS NOT NULL"
        ),
        "filename": "plantability.fgb",
    },
    "vegestrate": {
        "sql": ("SELECT id, geometry, strate, surface" " FROM iarbre_data_vegestrate"),
        "filename": "vegestrate.fgb",
    },
}


def _build_pg_connection_string() -> str:
    db = settings.DATABASES["default"]
    parts = [f"dbname={db['NAME']}", f"user={db['USER']}"]
    if db.get("PASSWORD"):
        parts.append(f"password={db['PASSWORD']}")
    if db.get("HOST"):
        parts.append(f"host={db['HOST']}")
    if db.get("PORT"):
        parts.append(f"port={db['PORT']}")
    return f"PG:{' '.join(parts)}"


def generate_flatgeobuf(dataset_name: str) -> str:
    """Generate a FlatGeobuf file for the given dataset.

    Returns the absolute path of the generated file.
    """
    config = DATASETS[dataset_name]
    output_dir = os.path.join(settings.MEDIA_ROOT, "vectors")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, config["filename"])

    # Remove existing file to avoid ogr2ogr append
    if os.path.exists(output_path):
        os.remove(output_path)

    pg_conn = _build_pg_connection_string()

    cmd = [
        "ogr2ogr",
        "-f",
        "FlatGeobuf",
        output_path,
        pg_conn,
        "-sql",
        config["sql"],
        "-nln",
        dataset_name,
        "-a_srs",
        "EPSG:2154",
    ]

    log_progress(f"Generating FlatGeobuf: {output_path}")
    subprocess.run(cmd, check=True)
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    log_progress(f"Generated {output_path} ({size_mb:.0f} MB)")
    return output_path


class Command(BaseCommand):
    help = "Export plantability/vegestrate vectors to FlatGeobuf (.fgb) files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dataset",
            choices=list(DATASETS.keys()),
            default=None,
            help="Export a single dataset. If omitted, exports all.",
        )

    def handle(self, *args, **options):
        datasets = [options["dataset"]] if options["dataset"] else list(DATASETS.keys())
        for name in datasets:
            start = time.monotonic()
            generate_flatgeobuf(name)
            elapsed = time.monotonic() - start
            self.stdout.write(
                self.style.SUCCESS(f"  {name} exported in {elapsed:.1f}s")
            )
