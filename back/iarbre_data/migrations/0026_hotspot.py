# Generated by Django 5.2.2 on 2025-06-30 09:50

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("iarbre_data", "0025_rename_commune_code_cadastre_city_code_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="HotSpot",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("geometry", django.contrib.gis.db.models.fields.PointField(srid=2154)),
                (
                    "map_geometry",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True, null=True, srid=3857
                    ),
                ),
                ("description", models.JSONField(blank=True, null=True)),
                ("city_name", models.CharField(blank=True, max_length=200, null=True)),
                (
                    "city",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hotspot",
                        to="iarbre_data.city",
                    ),
                ),
            ],
        ),
    ]
