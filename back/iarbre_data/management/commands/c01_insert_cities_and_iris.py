"""Insert cities and IRIS from geojson file and IGN WFS."""

import json
import logging

from django.contrib.gis.utils import LayerMapping
from django.core.management import BaseCommand
import requests
from django.db.models import QuerySet
from tqdm import tqdm
from django.contrib.gis.geos import GEOSGeometry
from unidecode import unidecode

from iarbre_data.models import City, Iris
from iarbre_data.utils.database import remove_duplicates
from iarbre_data.settings import SRID_DB

mapping_city = {"geometry": "POLYGON", "name": "nom", "code": "insee"}
mapping_iris = {"geometry": "POLYGON", "name": "iris_name", "code": "iris_code"}

IRIS_WFS_URL = "https://data.geopf.fr/wfs/ows"
IRIS_TYPENAME = "STATISTICALUNITS.IRIS:contours_iris"


class Command(BaseCommand):
    help = "Insert cities geojson file"

    @staticmethod
    def _insert_iris(qs_city: QuerySet) -> None:
        """Use IGN WFS to download IRIS and insert them in a table
        Args:
            qs_city (QuerySet): Query set that correspond to one or multiple cities.
        """
        for city in qs_city:
            print(f"Dowloading IRIS for city: {city.name}.")
            params = {
                "SERVICE": "WFS",
                "VERSION": "2.0.0",
                "REQUEST": "GetFeature",
                "TYPENAMES": IRIS_TYPENAME,
                "OUTPUTFORMAT": "application/json",
                "SRSNAME": f"EPSG:{SRID_DB}",
                "CQL_FILTER": f"code_insee='{city.code}'",
            }
            response = requests.get(IRIS_WFS_URL, params=params, timeout=60)
            response.raise_for_status()
            for feature in tqdm(response.json()["features"]):
                properties = feature["properties"]
                geom = GEOSGeometry(json.dumps(feature["geometry"]))
                geom.srid = SRID_DB
                if geom.geom_type == "MultiPolygon":
                    if geom.num_geom > 1:
                        print(
                            f"IRIS {properties['code_iris']} has {geom.num_geom} parts, "
                            "keeping the largest one."
                        )
                    geom = max(geom, key=lambda polygon: polygon.area)
                Iris.objects.update_or_create(
                    city_id=city.id,
                    code=properties["code_iris"],
                    defaults={"geometry": geom, "name": properties["nom_iris"]},
                )

    @staticmethod
    def _insert_cities(data: str) -> None:
        """Insert cities from a GEOJSON file.
        Args:
            data (str): path to the GEOJSON containing cities geometry.
        """
        lm = LayerMapping(City, data=data, mapping=mapping_city)
        lm.save()
        for city in City.objects.all():
            city.tiles_generated = False
            city.tiles_computed = False
            # Remove accents from city name and replace hyphens with spaces
            if city.name:
                city.name = unidecode(city.name).replace("-", " ").strip()
            city.save()

    def handle(self, *args, **options):
        """Insert cities from geojson file and IRIS from IGN WFS."""
        logger = logging.getLogger(__name__)
        self._insert_cities(data="file_data/communes_gl_2025.geojson")
        print("Removing duplicated cities...")
        remove_duplicates(City)
        logger.info("Duplicate removal complete.")
        qs_city = City.objects.all()
        self._insert_iris(qs_city=qs_city)
        print("Removing duplicated IRIS...")
        remove_duplicates(Iris)
