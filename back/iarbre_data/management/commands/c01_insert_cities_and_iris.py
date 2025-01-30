"""Insert cities and IRIS from geojson file and BPCE API."""
import logging

from django.contrib.gis.utils import LayerMapping
from django.core.management import BaseCommand
import requests
from tqdm import tqdm
from django.contrib.gis.geos import GEOSGeometry

from iarbre_data.models import City, Iris
from iarbre_data.management.commands.utils import (
    load_geodataframe_from_db,
    remove_duplicates,
)
from iarbre_data.settings import TARGET_PROJ

mapping_city = {"geometry": "POLYGON", "name": "nom", "code": "insee"}
mapping_iris = {"geometry": "POLYGON", "name": "iris_name", "code": "iris_code"}

api_url = "https://bpce.opendatasoft.com/api/explore/v2.1/catalog/datasets/iris-millesime-france/records"


class Command(BaseCommand):
    help = "Insert cities geojson file"

    @staticmethod
    def _insert_iris(qs_city) -> None:
        """Use BPCE API to download IRIS and insert them in a table
        Args:
            qs_city (QuerySet): Query set that correspond to one or multiple cities.
        """
        cities = load_geodataframe_from_db(qs_city, ["id", "name", "code"])
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

    @staticmethod
    def _insert_cities(data) -> None:
        """Insert cities from a GEOJSON file.
        Args:
            data (str): path to the GEOJSON containing cities geometry.
        """
        lm = LayerMapping(City, data=data, mapping=mapping_city)
        lm.save()
        for city in City.objects.all():
            city.tiles_generated = False
            city.tiles_computed = False
            city.save()

    def handle(self, *args, **options):
        """Insert cities from geojson file and IRIS from BPCE API."""
        logger = logging.getLogger(__name__)
        self._insert_cities(data="file_data/communes_gl_2025.geojson")
        print("Removing duplicated cities...")
        remove_duplicates(City)
        logger.info("Duplicate removal complete.")
        qs_city = City.objects.all()
        self._insert_iris(qs_city=qs_city)
        print("Removing duplicated IRIS...")
        remove_duplicates(Iris)
