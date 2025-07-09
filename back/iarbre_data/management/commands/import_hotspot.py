import time
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

    def extract_first_street_number(self, address):
        """Extract only the first street number from addresses with multiple numbers."""

        parts = address.split()

        first_part = parts[0]

        # Handle patterns like "43,45,47,49" or "121 A,B,C,D,E,F,G,H"
        if "," in first_part:
            first_number = first_part.split(",")[0]
            parts[0] = first_number

        # Handle patterns like "43/45/47" or "51,53,55 / 57,59,61,63"
        elif "/" in first_part:
            first_number = first_part.split("/")[0]
            parts[0] = first_number

        # Handle patterns where second part might contain letters like "A,B,C,D"
        elif (
            len(parts) > 1
            and "," in parts[1]
            and all(c.isalpha() or c == "," for c in parts[1])
        ):
            # Keep the number, remove the letter variations
            parts = [parts[0]] + parts[2:]

        return " ".join(parts)

    def clean_address(self, address):
        """Remove everything after postal code and extract first street number."""
        if not address:
            return address

        # First extract only the first street number
        address = self.extract_first_street_number(address)

        parts = address.split()
        for i, part in enumerate(parts):
            if part.isdigit() and len(part) == 5:
                # Keep everything up to and including the postal code
                return " ".join(parts[: i + 1])
        return address

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

    def find_address_column(self, df):
        """Find the address column in the dataframe."""
        for col in df.columns:
            if "adresse" in col.lower():
                if not df[col].isna().all():
                    return col
        return None

    def get_full_address(self, row, address_column, df):
        """Get full address by appending commune if it exists."""
        address = row[address_column]

        # Look for a Commune column
        commune_col = None
        for col in df.columns:
            if col.strip().lower() == "commune":
                commune_col = col
                break

        if commune_col and not pd.isna(row[commune_col]):
            commune = str(row[commune_col]).strip()
            if commune:
                if "lyon" in commune.lower():
                    parts = commune.split()
                    arrondissement = int(parts[1])
                    commune = f"690{arrondissement:02d}"
                address = f"{address}, {commune}"

        return address

    def get_additional_data_columns(self, df, address_column):
        """Get additional data columns after the address column."""
        additional_data = {}
        col_index = list(df.columns).index(address_column)
        for col in df.columns[col_index + 1 :]:
            if not df[col].isna().all():
                additional_data[col] = col
        return additional_data

    def build_description(self, sheet_name, row, additional_data):
        """Build description object from row data."""
        description = {"sheet": sheet_name}
        for col_name, col_key in additional_data.items():
            value = row[col_name]
            if not pd.isna(value):
                description[col_key] = value
        return description

    def extract_city_name_from_address(self, address):
        """Extract city name from address string."""
        parts = address.split()
        for i, part in enumerate(parts):
            if part.isdigit() and len(part) == 5:
                if i + 1 < len(parts):
                    return " ".join(parts[i + 1 :])
        return None

    def create_or_update_hotspot(self, geometry, description, city_name, city):
        """Create or update a HotSpot object."""
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
            return True
        except Exception as e:
            print(f"Error creating HotSpot: {e}")
            return False

    def process_sheet(self, file_path, sheet_name):
        """Process a single sheet from the Excel file."""
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        address_column = self.find_address_column(df)
        if not address_column:
            print(f'No address column found in sheet "{sheet_name}"')
            return 0

        additional_data = self.get_additional_data_columns(df, address_column)
        created_count = 0

        for _, row in df.iterrows():
            address = self.get_full_address(row, address_column, df)
            if pd.isna(address) or not address.strip():
                continue

            description = self.build_description(sheet_name, row, additional_data)
            geometry = geocode_address(address)
            time.sleep(1)  # 1 request max per second
            if not geometry:
                print(f"Could not geocode address {address}, skipping")
                continue

            city = self.get_city_from_address(address)
            city_name = (
                city.name if city else self.extract_city_name_from_address(address)
            )

            if self.create_or_update_hotspot(geometry, description, city_name, city):
                created_count += 1

        return created_count

    def handle(self, *args, **options):
        file_path = options["file"]

        try:
            xl_file = pd.ExcelFile(file_path)
            total_created = 0

            print(f"Found sheets: {xl_file.sheet_names}")
            print(xl_file.sheet_names)
            for sheet_name in xl_file.sheet_names:
                created = self.process_sheet(file_path, sheet_name)
                total_created += created
                print(f'Sheet "{sheet_name}": {created} HotSpots created')

            print(f"Total: {total_created} HotSpots created successfully")

        except Exception as e:
            print(f"ERROR: Error processing file: {e}")
