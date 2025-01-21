import logging

from django.contrib.gis.utils import LayerMapping
from django.core.management import BaseCommand
from django.db.models import Count
import requests
from tqdm import tqdm
from django.contrib.gis.geos import GEOSGeometry

from iarbre_data.models import City, Iris
from iarbre_data.management.commands.utils import load_geodataframe_from_db
from iarbre_data.settings import TARGET_PROJ

mapping_city = {"geometry": "POLYGON", "name": "nom", "code": "insee"}
mapping_iris = {"geometry": "POLYGON", "name": "iris_name", "code": "iris_code"}

api_url = "https://bpce.opendatasoft.com/api/explore/v2.1/catalog/datasets/iris-millesime-france/records"


class Command(BaseCommand):
    help = "Insert cities geojson file"

    @staticmethod
    def _remove_duplicates(Model):
        """Deletes duplicates in the instance model based on geometry."""
        duplicates = (
            Model.objects.values("geometry")
            .annotate(count=Count("id"))
            .filter(count__gt=1)
        )

        for duplicate in duplicates:
            geometry = duplicate["geometry"]
            duplicate_instances = Model.objects.filter(geometry=geometry)
            # Keep the first and delete the rest
            ids_to_delete = duplicate_instances.values_list("id", flat=True)[1:]
            Model.objects.filter(id__in=ids_to_delete).delete()
        print(f"Removed duplicates for {duplicates.count()} entries.")

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        lm = LayerMapping(City, "file_data/communes_gl_2025.geojson", mapping_city)
        lm.save()
        for city in City.objects.all():
            city.tiles_generated = False
            city.tiles_computed = False
            city.save()
        logger.info("Data insertion for city complete.")
        print("Removing duplicated cities...")
        self._remove_duplicates(City)
        logger.info("Duplicate removal complete.")

        cities = load_geodataframe_from_db(City.objects.all(), ["id", "name", "code"])
        limit = 100
        for city in cities.itertuples():
            city_GEOS = GEOSGeometry(city.geometry.wkt)
            city_GEOS.srid = TARGET_PROJ
            print(f"Dowloading IRIS for city: {city.name}.")
            if city.name[:4].upper() == "LYON":
                com_code = 69123
            else:
                com_code = city.code
            offset = 0
            params = {
                "where": f"com_code={int(com_code)}",
                "limit": limit,
                "offset": offset,
            }
            response = requests.get(api_url, params=params)
            while response.status_code == 200:
                data = response.json()
                records = data.get("results", [])
                if len(records) == 0:
                    break
                for record in tqdm(records, total=len(records)):
                    geometry = record["geo_shape"]["geometry"]
                    iris_name = record.get("iris_name")[0]
                    iris_code = record.get("iris_code")[0]
                    if geometry and iris_name and iris_code:
                        geom = GEOSGeometry(str(geometry))
                        geom.transform(TARGET_PROJ, clone=False)
                        if geom.intersects(
                            city_GEOS
                        ):  # for Lyon keep only iris for the 'arrondissement' at hand
                            Iris.objects.update_or_create(
                                city_id=city.id,
                                code=iris_code,
                                defaults={
                                    "geometry": geom,
                                    "name": iris_name,
                                },
                            )
                    else:
                        print("No Iris code")
                # Iteration over next fetch
                offset += limit
                params = {
                    "where": f"com_code={int(com_code)}",
                    "limit": limit,
                    "offset": offset,
                }
                response = requests.get(api_url, params=params)
        print("Removing duplicated IRIS...")
        self._remove_duplicates(Iris)
