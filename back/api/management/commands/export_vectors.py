"""Export plantability and vegestrate vector data to downloadable files.

Supported formats:
  - **FlatGeobuf** (.fgb): via ogr2ogr, streaming from PostGIS with zero
    memory overhead. Includes a packed Hilbert R-tree spatial index for
    HTTP range-request streaming in QGIS.
  - **GeoParquet** (.parquet): via geopandas + pyarrow, written in chunked
    row groups to bound memory usage. Columnar format, efficient for large
    analytical queries.

Usage:
    python manage.py export_vectors
    python manage.py export_vectors --dataset plantability
    python manage.py export_vectors --format geoparquet
    python manage.py export_vectors --format flatgeobuf --dataset vegestrate
"""

import logging
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from django.conf import settings
from django.db import connection
from django.core.management import BaseCommand

from iarbre_data.models import Tile, Vegestrate
from iarbre_data.settings import SRID_DB
from iarbre_data.utils.database import load_geodataframe_from_db

logger = logging.getLogger(__name__)

VECTORS_DIR = "vectors"
PARQUET_CHUNK_SIZE = 500_000

FORMAT_EXTENSIONS = {
    "flatgeobuf": ".fgb",
    "geoparquet": ".parquet",
}

DATASETS = {
    "plantability": {
        "queryset": Tile.objects.filter(plantability_normalized_indice__isnull=False),
        "fields": ["plantability_indice", "plantability_normalized_indice"],
        "geometry_type": "POLYGON",
    },
    "vegestrate": {
        "queryset": Vegestrate.objects.all(),
        "fields": ["strate", "surface"],
        "geometry_type": "POLYGON",
    },
}


def get_vector_file_map(fmt: str) -> dict[str, tuple[str, str]]:
    """Build the file map for a given format, used by download views."""
    ext = FORMAT_EXTENSIONS[fmt]
    return {name: (f"{VECTORS_DIR}/{name}{ext}", f"{name}{ext}") for name in DATASETS}


# -- Helpers -----------------------------------------------------------------


def _queryset_to_sql(queryset, extra_fields: list[str]) -> str:
    """Build a raw SQL SELECT from a Django queryset for ogr2ogr.

    Uses the Django ORM compiler to extract a reliable WHERE clause
    instead of string-splitting the full query.
    """
    fields = ", ".join(["id", "geometry", *extra_fields])
    table = queryset.model._meta.db_table

    compiler = queryset.query.get_compiler(using="default")
    where_node = queryset.query.where
    if where_node.children:
        where_sql, where_params = compiler.compile(where_node)
        with connection.cursor() as cursor:
            where_clause = " WHERE " + cursor.mogrify(where_sql, where_params).decode()
    else:
        where_clause = ""

    return f"SELECT {fields} FROM {table}{where_clause}"


def _output_path(dataset_name: str, fmt: str) -> Path:
    output_dir = Path(settings.MEDIA_ROOT) / VECTORS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{dataset_name}{FORMAT_EXTENSIONS[fmt]}"


def _atomic_tmp_path(output_dir: Path, dataset_name: str, ext: str) -> Path:
    """Reserve a unique temp path in the same directory for atomic replace.

    The file is created then immediately deleted so ogr2ogr / pyarrow can
    create it themselves.
    """
    tmp_fd, tmp_path_str = tempfile.mkstemp(
        suffix=ext, dir=output_dir, prefix=f".{dataset_name}_"
    )
    os.close(tmp_fd)
    tmp_path = Path(tmp_path_str)
    tmp_path.unlink()
    return tmp_path


# -- FlatGeobuf (ogr2ogr) ---------------------------------------------------


def _generate_flatgeobuf(dataset_name: str) -> Path:
    if shutil.which("ogr2ogr") is None:
        raise RuntimeError("ogr2ogr is not installed. Run: apt install gdal-bin")

    config = DATASETS[dataset_name]
    sql = _queryset_to_sql(config["queryset"], config["fields"])
    output_path = _output_path(dataset_name, "flatgeobuf")
    tmp_path = _atomic_tmp_path(output_path.parent, dataset_name, ".fgb")

    db = settings.DATABASES["default"]
    pg_parts = [f"dbname={db['NAME']}", f"user={db['USER']}"]
    if db.get("HOST"):
        pg_parts.append(f"host={db['HOST']}")
    if db.get("PORT"):
        pg_parts.append(f"port={db['PORT']}")

    env = os.environ.copy()
    if db.get("PASSWORD"):
        env["PGPASSWORD"] = db["PASSWORD"]

    cmd = [
        "ogr2ogr",
        "-f",
        "FlatGeobuf",
        str(tmp_path),
        f"PG:{' '.join(pg_parts)}",
        "-sql",
        sql,
        "-nln",
        dataset_name,
        "-nlt",
        config["geometry_type"],
        "-a_srs",
        f"EPSG:{SRID_DB}",
    ]

    try:
        subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        tmp_path.unlink(missing_ok=True)
        raise RuntimeError(f"ogr2ogr failed for {dataset_name}: {exc.stderr}") from exc

    os.replace(tmp_path, output_path)
    return output_path


# -- GeoParquet (geopandas + pyarrow) ----------------------------------------


def _generate_geoparquet(dataset_name: str) -> Path:
    """Export via Django ORM + geopandas/pyarrow in chunked row groups.

    The first chunk is serialized via geopandas.to_parquet (BytesIO) to
    obtain an Arrow schema that includes the ``geo`` metadata key required
    by geopandas.read_parquet. Subsequent chunks use the faster
    gdf.to_arrow()._pa_table path and are cast to the reference schema.
    """
    import io
    import pyarrow.parquet as pq

    config = DATASETS[dataset_name]
    queryset = config["queryset"].order_by("pk")
    fields = ["id", *config["fields"]]
    total = queryset.count()

    output_path = _output_path(dataset_name, "geoparquet")
    tmp_path = _atomic_tmp_path(output_path.parent, dataset_name, ".parquet")

    writer = None
    out_file = None
    schema = None
    written = 0

    try:
        while written < total:
            chunk_qs = queryset[written : written + PARQUET_CHUNK_SIZE]
            gdf = load_geodataframe_from_db(chunk_qs, list(fields))
            if gdf.empty:
                break

            if schema is None:
                # First chunk: round-trip via BytesIO to capture geo metadata
                buf = io.BytesIO()
                gdf.to_parquet(buf)
                buf.seek(0)
                table = pq.read_table(buf)
                schema = table.schema
                out_file = tmp_path.open("wb")
                writer = pq.ParquetWriter(out_file, schema)
            else:
                # Subsequent chunks: direct Arrow conversion (no serde overhead)
                table = gdf.to_arrow()._pa_table.cast(schema)

            writer.write_table(table)
            written += len(gdf)
            logger.info("  %s: %d / %d features written", dataset_name, written, total)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise
    finally:
        if writer is not None:
            writer.close()
        if out_file is not None:
            out_file.close()

    os.replace(tmp_path, output_path)
    return output_path


# -- Public API --------------------------------------------------------------


def generate_vector_export(dataset_name: str, fmt: str = "flatgeobuf") -> Path:
    """Generate a vector export file for the given dataset and format."""
    logger.info("Generating %s: %s", fmt, dataset_name)

    if fmt == "flatgeobuf":
        path = _generate_flatgeobuf(dataset_name)
    elif fmt == "geoparquet":
        path = _generate_geoparquet(dataset_name)
    else:
        raise ValueError(f"Unknown format: {fmt}")

    size_mb = path.stat().st_size / (1024 * 1024)
    logger.info("Generated %s (%.0f MB)", path, size_mb)
    return path


class Command(BaseCommand):
    help = "Export plantability/vegestrate vectors to FlatGeobuf or GeoParquet."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dataset",
            choices=list(DATASETS.keys()),
            default=None,
            help="Export a single dataset. If omitted, exports all.",
        )
        parser.add_argument(
            "--format",
            choices=list(FORMAT_EXTENSIONS.keys()),
            default="flatgeobuf",
            help="Output format (default: flatgeobuf).",
        )

    def handle(self, *args, **options):
        fmt = options["format"]
        datasets = [options["dataset"]] if options["dataset"] else list(DATASETS.keys())
        for name in datasets:
            start = time.monotonic()
            path = generate_vector_export(name, fmt)
            elapsed = time.monotonic() - start
            self.stdout.write(
                self.style.SUCCESS(f"  {name} ({fmt}) -> {path} in {elapsed:.1f}s")
            )
