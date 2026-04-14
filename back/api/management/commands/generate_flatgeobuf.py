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

import logging
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand

from iarbre_data.models import Tile, Vegestrate

logger = logging.getLogger(__name__)

VECTORS_DIR = "vectors"


def _queryset_to_sql(queryset, extra_fields: list[str]) -> str:
    """Build a raw SQL SELECT from a Django queryset for ogr2ogr.

    Always includes ``id`` and ``geometry``, plus any extra fields.
    """
    fields = ", ".join(["id", "geometry", *extra_fields])
    # queryset.query gives the full WHERE / FROM clause
    qs_sql = str(queryset.values("id").query)
    table = queryset.model._meta.db_table
    # Extract WHERE clause if present
    where = ""
    if " WHERE " in qs_sql:
        where = " WHERE " + qs_sql.split(" WHERE ", 1)[1]
    return f"SELECT {fields} FROM {table}{where}"


DATASETS = {
    "plantability": {
        "queryset": Tile.objects.filter(plantability_normalized_indice__isnull=False),
        "fields": ["plantability_indice", "plantability_normalized_indice"],
        "filename": "plantability.fgb",
    },
    "vegestrate": {
        "queryset": Vegestrate.objects.all(),
        "fields": ["strate", "surface"],
        "filename": "vegestrate.fgb",
    },
}


def _build_ogr2ogr_env() -> tuple[str, dict]:
    """Build a PG connection string and an env dict with PGPASSWORD.

    The password is passed via the PGPASSWORD environment variable instead of
    embedding it in the connection string, keeping it out of the process
    argument list visible via ``ps``.
    """
    db = settings.DATABASES["default"]
    parts = [f"dbname={db['NAME']}", f"user={db['USER']}"]
    if db.get("HOST"):
        parts.append(f"host={db['HOST']}")
    if db.get("PORT"):
        parts.append(f"port={db['PORT']}")

    import os

    env = os.environ.copy()
    if db.get("PASSWORD"):
        env["PGPASSWORD"] = db["PASSWORD"]

    return f"PG:{' '.join(parts)}", env


def generate_flatgeobuf(dataset_name: str) -> Path:
    """Generate a FlatGeobuf file for the given dataset.

    Writes to a temporary file first, then renames atomically so a partial
    file is never served if the process crashes mid-export.

    Returns the path of the generated file.
    """
    if shutil.which("ogr2ogr") is None:
        raise RuntimeError(
            "ogr2ogr is not installed or not in PATH. "
            "Install GDAL CLI tools (apt install gdal-bin / brew install gdal)."
        )

    config = DATASETS[dataset_name]
    sql = _queryset_to_sql(config["queryset"], config["fields"])
    output_dir = Path(settings.MEDIA_ROOT) / VECTORS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / config["filename"]

    pg_conn, env = _build_ogr2ogr_env()

    # Write to a temp file in the same directory (same filesystem) so
    # os.replace() is atomic.
    tmp_fd, tmp_path = tempfile.mkstemp(
        suffix=".fgb", dir=output_dir, prefix=f".{dataset_name}_"
    )
    # mkstemp opens the fd; close it so ogr2ogr can write.
    import os

    os.close(tmp_fd)

    cmd = [
        "ogr2ogr",
        "-f",
        "FlatGeobuf",
        tmp_path,
        pg_conn,
        "-sql",
        sql,
        "-nln",
        dataset_name,
        "-a_srs",
        "EPSG:2154",
    ]

    logger.info("Generating FlatGeobuf: %s", output_path)
    try:
        subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        Path(tmp_path).unlink(missing_ok=True)
        logger.error("ogr2ogr failed:\n%s", exc.stderr)
        raise RuntimeError(f"ogr2ogr failed for {dataset_name}: {exc.stderr}") from exc

    # Atomic replace
    os.replace(tmp_path, output_path)
    size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info("Generated %s (%.0f MB)", output_path, size_mb)
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
            path = generate_flatgeobuf(name)
            elapsed = time.monotonic() - start
            self.stdout.write(
                self.style.SUCCESS(f"  {name} exported to {path} in {elapsed:.1f}s")
            )
