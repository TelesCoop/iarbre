from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("iarbre_data", "0046_merge_20261021_0826"),
    ]

    operations = [
        migrations.RenameField(
            model_name="vegestrate",
            old_name="mean_height",
            new_name="median_height",
        ),
    ]
