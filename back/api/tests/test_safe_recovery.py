import os
import tempfile
from unittest import mock

from django.core.management import call_command
from django.db import connection
from django.test import TransactionTestCase

from api.management.commands.safe_recovery import Command
from api.models import Feedback, ShortLink


class SafeRecoveryTest(TransactionTestCase):
    def test_rows_survive_a_wiped_database(self):
        Feedback.objects.create(feedback="Raise the floor")
        ShortLink.objects.create(code="abc12345", path="/plantability/14/45.0/4.0")

        with tempfile.TemporaryDirectory() as tmp_dir:
            backup_file = os.path.join(tmp_dir, "model_backup.sql")
            with mock.patch.object(Command, "backup_file", backup_file):
                call_command("safe_recovery", "backup")
                with connection.cursor() as cursor:
                    cursor.execute("TRUNCATE api_feedback, api_shortlink")
                call_command("safe_recovery", "restore")
            self.assertFalse(os.path.exists(backup_file))

        self.assertEqual(Feedback.objects.get().feedback, "Raise the floor")
        self.assertEqual(ShortLink.objects.get().code, "abc12345")
        link_after_restore = ShortLink.objects.create(code="new12345", path="/")
        self.assertIsNotNone(link_after_restore.pk)
