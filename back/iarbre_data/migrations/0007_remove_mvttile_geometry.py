# Generated by Django 5.1.3 on 2024-12-20 10:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("iarbre_data", "0006_alter_tilefactor_tile"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mvttile",
            name="geometry",
        ),
    ]
