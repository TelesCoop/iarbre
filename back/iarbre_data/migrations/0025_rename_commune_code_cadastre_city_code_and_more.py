# Generated by Django 5.2.2 on 2025-06-16 12:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("iarbre_data", "0024_alter_mvttile_datatype_alter_mvttile_geolevel_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="cadastre",
            old_name="commune_code",
            new_name="city_code",
        ),
        migrations.RenameField(
            model_name="cadastre",
            old_name="commune_name",
            new_name="city_name",
        ),
    ]
