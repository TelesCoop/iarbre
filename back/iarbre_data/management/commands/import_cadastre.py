import requests
from django.core.management import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from tqdm import tqdm

from iarbre_data.models import City, Cadastre
from iarbre_data.settings import TARGET_PROJ


class Command(BaseCommand):
    help = "Download and import cadastre data for all cities in Lyon metropolitan area"

    def add_arguments(self, parser):
        parser.add_argument(
            "--city-code",
            type=str,
            help="Import cadastre for specific city code only",
        )
        parser.add_argument(
            "--clean",
            action="store_true",
            help="Clean existing cadastre data before import",
        )

    def handle(self, *args, **options):
        if options["clean"]:
            print("Cleaning existing cadastre data...")
            Cadastre.objects.all().delete()

        if options["city_code"]:
            cities = City.objects.filter(code=options["city_code"])
            if not cities.exists():
                print(f"No city found with code {options['city_code']}")
                return
        else:
            cities = City.objects.all()

        print(f"Processing {cities.count()} cities...")

        for city in tqdm(cities, desc="Processing cities"):
            try:
                self.import_cadastre_for_city(city)
            except Exception as e:
                print(f"Error processing city {city.name}: {e}")

    def import_cadastre_for_city(self, city):
        print(f"Downloading cadastre for {city.name} ({city.code})...")

        url = f"https://cadastre.data.gouv.fr/bundler/cadastre-etalab/communes/{city.code}/geojson/parcelles"

        response = requests.get(url)
        response.raise_for_status()

        geojson_data = response.json()
        if geojson_data.get("type") != "FeatureCollection":
            print(f"No cadastre data found for {city.name}")
            return

        source_srid = 4326

        features = geojson_data.get("features", [])
        print(f"Found {len(features)} parcels for {city.name}")

        parcels_created = 0
        for feature in tqdm(
            features, desc=f"Importing parcels for {city.name}", leave=False
        ):
            try:
                properties = feature.get("properties", {})
                geometry_data = feature.get("geometry")

                if not geometry_data:
                    continue

                geometry = GEOSGeometry(str(geometry_data))
                geometry.srid = source_srid
                if source_srid != TARGET_PROJ:
                    geometry.transform(TARGET_PROJ)

                if not geometry.valid:
                    try:
                        geometry = geometry.buffer(0)
                    except Exception as e:
                        print("Geometry not valid", e)
                        continue

                parcel_id = properties.get("id")
                if not parcel_id:
                    continue

                existing_parcel = Cadastre.objects.filter(parcel_id=parcel_id).first()
                if existing_parcel:
                    continue

                Cadastre.objects.create(
                    geometry=geometry,
                    parcel_id=parcel_id,
                    city_code=properties.get("commune", city.code),
                    city_name=city.name,
                    section=properties.get("section"),
                    numero=properties.get("numero"),
                    surface=properties.get("contenance"),
                    city=city,
                )
                parcels_created += 1

            except Exception as e:
                print(f"Error importing parcel: {e}")
                continue

        print(f"Successfully imported {parcels_created} parcels for {city.name}")
