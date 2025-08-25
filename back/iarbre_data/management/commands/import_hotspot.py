import time
import pandas as pd
import re
from django.core.management.base import BaseCommand
from iarbre_data.models import HotSpot, City
from iarbre_data.utils.data_processing import geocode_address
from unidecode import unidecode


class Command(BaseCommand):
    help = "Import hotspot data from Excel file with address geocoding"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="file_data/hotspot/private_trees.xlsx",
            help="Path to the Excel file to import (default: file_data/hotspot/private_trees.xlsx)",
        )

    @staticmethod
    def extract_first_street_number(address):
        """Extract only the first street number and the first street name from the address."""
        # Find the first number in the address
        match = re.search(r"\d+", address)
        if not match:
            return address  # No number found, return as-is

        first_number = match.group()

        first_number_index = address.find(first_number)
        rest_of_address = address[first_number_index + len(first_number) :]

        # Remove everything before the actual street name (keep everything from first proper word)
        match = re.search(r"[A-Z][A-Z]+(?:\s+[A-Z]+)*", rest_of_address)
        if match:
            rest_of_address = rest_of_address[match.start() :]

        rest_of_address = re.sub(r"/\s*", " ", rest_of_address)
        parts = rest_of_address.split(",")
        if len(parts) > 1:
            result_parts = [parts[0]]
            for part in parts[1:]:
                if re.match(r"\s*\d", part):  # Part starts with digits (postal code)
                    result_parts.append("," + part)
                else:
                    result_parts.append(" " + part)
            rest_of_address = "".join(result_parts)
        rest_of_address = " ".join(rest_of_address.split())

        modified_address = f"{first_number} {rest_of_address}"

        return modified_address.strip()

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
                    city_name = city_name.replace("-", " ").strip()
                    if city_name.lower() == "lyon":
                        arrondissement = part[-2:]
                        city_name = f"{city_name} {arrondissement.lstrip('0')}"
                    break
        if city_name:
            try:
                return City.objects.filter(name__icontains=unidecode(city_name)).first()
            except Exception as e:
                print(f"Can't find City {city_name}: {e}.")
                return None
        return None

    def find_column(self, df: pd.DataFrame, regex: str):
        """Find the a column in the dataframe based on regex."""
        for col in df.columns:
            if regex in col.lower():
                if not df[col].isna().all():
                    return col
        return None

    def get_full_address(self, row, address_column, df):
        """Get full address by appending commune if it exists."""
        address = row[address_column]
        commune_col = self.find_column(df, "commune")

        if commune_col and not pd.isna(row[commune_col]):
            commune = str(row[commune_col]).strip()
            if commune:
                if ("lyon" in commune.lower()) and not (
                    "foy" in commune.lower()
                ):  # Sainte-For-lès-lyon
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

    def create_or_update_hotspot(self, geometry, description, city_name, city):
        """Create or update a HotSpot object."""
        if city is None:
            breakpoint()
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
        address_column = self.find_column(df, "adresse")
        commune_column = self.find_column(df, "commune")
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
            geometry = geocode_address(self.clean_address(address))
            time.sleep(1)  # 1 request max per second
            if not geometry:
                print("*" * 10)
                print(f"Could not geocode address {address}, skipping")
                print("*" * 10)
                continue
            city = self.get_city_from_address(address)

            if city is None:
                city = City.objects.filter(
                    name__icontains=unidecode(
                        row[commune_column].replace("-", " ").strip()
                    )
                ).first()
            city_name = city.name
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
                print(f'Sheet "{sheet_name}"')
                created = self.process_sheet(file_path, sheet_name)
                total_created += created
                print(f'Sheet "{sheet_name}": {created} HotSpots created')

            print(f"Total: {total_created} HotSpots created successfully")

        except Exception as e:
            print(f"ERROR: Error processing file: {e}")
