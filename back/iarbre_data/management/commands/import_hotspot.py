import pandas as pd
from django.core.management.base import BaseCommand
from iarbre_data.models import HotSpot, City
from iarbre_data.utils.data_processing import geocode_address


class Command(BaseCommand):
    help = "Import hotspot data from Excel file with address geocoding"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="file_data/hotspot/private_trees.xlsx",
            help="Path to the Excel file to import (default: file_data/hotspot/private_trees.xlsx)",
        )

    def get_city_from_address(self, address):
        """Extract city from address and find matching City object."""
        parts = address.split()
        city_name = None

        for i, part in enumerate(parts):
            if part.isdigit() and len(part) == 5:
                if i + 1 < len(parts):
                    city_name = " ".join(parts[i + 1 :])
                    break

        if city_name:
            try:
                return City.objects.filter(name__icontains=city_name).first()
            except Exception as e:
                print(f"Can't find City {city_name}: {e}.")
                return None

        return None

    def process_sheet(self, file_path, sheet_name):
        """Process a single sheet from the Excel file."""
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        address_column = None
        for col in df.columns:
            if "adresse" in col.lower() or col == "Unnamed: 0":
                if not df[col].isna().all():
                    address_column = col
                    break

        if not address_column:
            print(f'No address column found in sheet "{sheet_name}"')
            return 0

        additional_data = {}
        col_index = list(df.columns).index(address_column)
        for col in df.columns[col_index + 1 :]:
            if not df[col].isna().all():
                additional_data[col] = col

        created_count = 0

        for _, row in df.iterrows():
            address = row[address_column]

            if pd.isna(address) or not address.strip():
                continue

            description = {"sheet": sheet_name}
            for col_name, col_key in additional_data.items():
                value = row[col_name]
                if not pd.isna(value):
                    description[col_key] = value

            geometry = geocode_address(address)

            if not geometry:
                print(f"Could not geocode address {address}, skipping")
                continue

            city = self.get_city_from_address(address)
            city_name = None
            if city:
                city_name = city.name
            else:
                parts = address.split()
                for i, part in enumerate(parts):
                    if part.isdigit() and len(part) == 5:
                        if i + 1 < len(parts):
                            city_name = " ".join(parts[i + 1 :])
                            break

            try:
                hotspot, created = HotSpot.objects.get_or_create(
                    geometry=geometry,
                    defaults={
                        "description": description,
                        "city_name": city_name,
                        "city": city,
                    },
                )
                if not created:
                    hotspot.description = description
                    hotspot.city_name = city_name
                    hotspot.city = city
                    hotspot.save()
                created_count += 1

            except Exception as e:
                print(f"Error creating HotSpot: {e}")

        return created_count

    def handle(self, *args, **options):
        file_path = options["file"]

        try:
            xl_file = pd.ExcelFile(file_path)
            total_created = 0

            print(f"Found sheets: {xl_file.sheet_names}")

            for sheet_name in xl_file.sheet_names:
                created = self.process_sheet(file_path, sheet_name)
                total_created += created
                print(f'Sheet "{sheet_name}": {created} HotSpots created')

            print(f"Total: {total_created} HotSpots created successfully")

        except Exception as e:
            print(f"ERROR: Error processing file: {e}")
