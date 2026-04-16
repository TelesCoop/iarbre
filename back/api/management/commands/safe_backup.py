from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Safely backup the database. Removes any test data created by the "
        "populate command before triggering the actual backup, so the "
        "uploaded backup never contains development/test fixtures."
    )

    def handle(self, *args, **options):
        self.stdout.write("Removing test data before backup...")
        call_command("delete_test_data")
        self.stdout.write("Running database backup...")
        call_command("backup_db", "backup")
        self.stdout.write(self.style.SUCCESS("Backup completed safely."))
