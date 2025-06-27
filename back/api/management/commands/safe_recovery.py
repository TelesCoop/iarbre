from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os
import subprocess

from api.models import Feedback


class Command(BaseCommand):
    help = "Safely recover database with model backup and restore using pg_dump"

    model_to_backup_before_recovery = [Feedback]
    backup_dir = os.path.join(settings.BASE_DIR, "tmp/backups", "model_backups")

    def get_db_settings(self):
        """Extract and return database settings as a dictionary"""
        db_settings = settings.DATABASES["default"]
        return {
            "NAME": db_settings["NAME"],
            "USER": db_settings["USER"],
            "PASSWORD": db_settings.get("PASSWORD", ""),
            "HOST": db_settings.get("HOST", "localhost"),
            "PORT": db_settings.get("PORT", "5432"),
        }

    def backup_models(self):
        """Backup specific models using pg_dump"""

        os.makedirs(self.backup_dir, exist_ok=True)

        db_settings = self.get_db_settings()
        backup_file = os.path.join(self.backup_dir, "model_backup.sql")

        # Build the pg_dump command
        pg_dump_cmd = [
            "pg_dump",
            "-h",
            db_settings["HOST"],
            "-p",
            db_settings["PORT"],
            "-U",
            db_settings["USER"],
            "-d",
            db_settings["NAME"],
            "-t",
            ",".join(
                [model._meta.db_table for model in self.model_to_backup_before_recovery]
            ),
            "-F",
            "p",  # plain SQL format
            "-f",
            backup_file,
        ]

        # Set the password environment variable
        env = os.environ.copy()
        env["PGPASSWORD"] = db_settings["PASSWORD"]

        try:
            # Execute the pg_dump command
            subprocess.run(
                pg_dump_cmd,
                check=True,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.stdout.write(f"Successfully backed up models to {backup_file}")
        except subprocess.CalledProcessError as e:
            self.stderr.write(
                self.style.ERROR(f"Error backing up database: {e.stderr.decode()}")
            )

    def restore_models(self):
        """Restore models from SQL backup file"""

        backup_file = os.path.join(self.backup_dir, "model_backup.sql")

        if not os.path.exists(backup_file):
            self.stdout.write(
                self.style.ERROR(f"No backup file found at {backup_file}")
            )
            return

        db_settings = self.get_db_settings()

        # Build the psql command for restoration
        psql_cmd = [
            "psql",
            "-h",
            db_settings["HOST"],
            "-p",
            db_settings["PORT"],
            "-U",
            db_settings["USER"],
            "-d",
            db_settings["NAME"],
            "-f",
            backup_file,
        ]

        # Set the password environment variable
        env = os.environ.copy()
        env["PGPASSWORD"] = db_settings["PASSWORD"]

        try:
            # Execute the psql command
            subprocess.run(
                psql_cmd,
                check=True,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.stdout.write("Successfully restored models from backup")
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f"Error restoring database: {e.stderr.decode()}")
            )

    def handle(self, *args, **options):
        # Backup models before recovery to avoid data loss
        self.backup_models()
        # Perform python manage.py backup_db recover_db_and_media
        call_command("backup_db", "recover_db_and_media")
        # Restore models after recovery
        self.restore_models()
