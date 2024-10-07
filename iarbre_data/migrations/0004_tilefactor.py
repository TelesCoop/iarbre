# Generated by Django 5.1 on 2024-08-18 13:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("iarbre_data", "0003_alter_tile_indice"),
    ]

    operations = [
        migrations.CreateModel(
            name="TileFactor",
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
                ("factor", models.CharField(max_length=50)),
                ("value", models.FloatField()),
                (
                    "tile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="iarbre_data.tile",
                    ),
                ),
            ],
        ),
    ]
