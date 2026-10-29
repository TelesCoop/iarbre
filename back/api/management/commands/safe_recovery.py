import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.db import connection

from api.models import Feedback, ShortLink


class Command(BaseCommand):
    help = (
        "Keep user-generated models (Feedback, ShortLink) across a database recovery: "
        "'backup' dumps their rows before the recovery, 'restore' reloads them after migrate."
    )

    models_to_keep = [Feedback, ShortLink]
    backup_file = os.path.join(
        settings.BASE_DIR, "tmp/backups", "model_backups", "model_backup.sql"
    )

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["backup", "restore"])

    def run_pg(self, cmd):
        db = settings.DATABASES["default"]
        env = {**os.environ, "PGPASSWORD": db.get("PASSWORD", "")}
        cmd += [
            "-h",
            db.get("HOST") or "localhost",
            "-p",
            str(db.get("PORT") or "5432"),
            "-U",
            db["USER"],
            "-d",
            db["NAME"],
        ]
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            raise CommandError(result.stderr)

    def backup(self):
        existing = set(connection.introspection.table_names())
        tables = [
            m._meta.db_table
            for m in self.models_to_keep
            if m._meta.db_table in existing
        ]
        if os.path.exists(self.backup_file):
            self.stdout.write(
                f"{self.backup_file} already exists (previous restore not completed), keeping it"
            )
            return
        if not tables:
            self.stdout.write("No table to back up")
            return
        os.makedirs(os.path.dirname(self.backup_file), exist_ok=True)
        table_args = [arg for table in tables for arg in ("-t", table)]
        self.run_pg(["pg_dump", "--data-only", *table_args, "-f", self.backup_file])
        self.stdout.write(f"Backed up {', '.join(tables)} to {self.backup_file}")

    def restore(self):
        if not os.path.exists(self.backup_file):
            self.stdout.write("No backup file, nothing to restore")
            return
        tables = ", ".join(m._meta.db_table for m in self.models_to_keep)
        with connection.cursor() as cursor:
            cursor.execute(f"TRUNCATE {tables}")
        self.run_pg(["psql", "-v", "ON_ERROR_STOP=1", "-f", self.backup_file])
        with connection.cursor() as cursor:
            for sql in connection.ops.sequence_reset_sql(
                no_style(), self.models_to_keep
            ):
                cursor.execute(sql)
        os.remove(self.backup_file)
        self.stdout.write(f"Restored {tables}")

    def handle(self, *args, **options):
        getattr(self, options["action"])()
