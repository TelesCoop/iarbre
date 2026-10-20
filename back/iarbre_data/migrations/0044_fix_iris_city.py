from django.db import migrations


def attach_iris_to_city_of_their_code(apps, _):
    City = apps.get_model("iarbre_data", "City")
    Iris = apps.get_model("iarbre_data", "Iris")
    city_ids = dict(City.objects.values_list("code", "id"))

    irises = list(Iris.objects.exclude(code=None))
    for iris in irises:
        iris.city_id = city_ids.get(iris.code[:5], iris.city_id)
    Iris.objects.bulk_update(irises, ["city"], batch_size=1000)


class Migration(migrations.Migration):

    dependencies = [
        ("iarbre_data", "0043_vegestrate_mean_height"),
    ]

    operations = [
        migrations.RunPython(
            attach_iris_to_city_of_their_code, migrations.RunPython.noop
        ),
    ]
