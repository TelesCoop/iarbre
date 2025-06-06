"""Utils to interact with the DB using Django."""

from datetime import datetime
from django.db.models import Count
from django.contrib.gis.db.models.functions import AsGeoJSON
from shapely.geometry import shape
import json

from iarbre_data.models import City
import geopandas as gpd

from iarbre_data.settings import TARGET_PROJ, TARGET_MAP_PROJ


def load_geodataframe_from_db(queryset, fields):
    """
    Load a GeoDataFrame from a Django model queryset.

    Args:
        queryset (QuerySet): Django queryset to load data from.
        fields (list[str]): List of fields to include in the GeoDataFrame.

    Returns:
        df (GeoDataFrame): GeoDataFrame with data from the queryset.
    """
    if not queryset.exists():
        return gpd.GeoDataFrame(columns=fields + ["geometry"])
    geom_field = "geometry"
    crs = TARGET_PROJ
    if "map_geometry" in fields:
        fields.remove("map_geometry")
        geom_field = "map_geometry"
        crs = TARGET_MAP_PROJ
    # Get geometry data in GEOJSON to avoid conversion to WKT with shapely
    qs = queryset.annotate(geom_json=AsGeoJSON(geom_field)).values(*fields, "geom_json")
    data = list(qs)  # Run query

    for row in data:
        row["geometry"] = shape(json.loads(row.pop("geom_json")))

    df = gpd.GeoDataFrame(data)
    df.set_geometry("geometry", inplace=True)
    df.crs = crs
    return df


def remove_duplicates(Model) -> None:
    """Deletes duplicates in the instance model based on geometry.
    Args:
        Model (class): iarbre_data.models in which duplicates are removed
    """
    duplicates = (
        Model.objects.values("geometry").annotate(count=Count("id")).filter(count__gt=1)
    )

    for duplicate in duplicates:
        geometry = duplicate["geometry"]
        duplicate_instances = Model.objects.filter(geometry=geometry)
        # Keep the first and delete the rest
        ids_to_delete = duplicate_instances.values_list("id", flat=True)[1:]
        Model.objects.filter(id__in=ids_to_delete).delete()
    print(f"Removed duplicates for {duplicates.count()} entries.")


def select_city(insee_code_city: str) -> gpd.GeoDataFrame:
    """Select a list of cities based on INSEE_CODE.

    Args:
        insee_code_city (str): INSEE code of the city or cities to select.

    Returns:
        selected_city (GeoDataFrame): GeoDataFrame containing the selected city or cities.
    """
    if insee_code_city is not None:  # Perform selection only for a city
        insee_code_city = insee_code_city.split(",")
        selected_city_qs = City.objects.filter(code__in=insee_code_city)
        if not selected_city_qs.exists():
            raise ValueError(f"No city found with INSEE code {insee_code_city}")
        selected_city = load_geodataframe_from_db(
            selected_city_qs,
            ["id", "name", "code", "tiles_generated", "tiles_computed"],
        )
    else:
        selected_city = load_geodataframe_from_db(
            City.objects.all(),
            ["id", "name", "code", "tiles_generated", "tiles_computed"],
        )
    return selected_city


def log_progress(step: str, star=False) -> None:
    """
    Log the progress of a step with a timestamp.

    Args:
        step (str): The description of the step being logged.
        star (bool): Print or not a line of stars
    """
    print(f"{datetime.now().strftime('%H:%M:%S')} - {step}")
    if star:
        print("*" * 30 + "\n")
        print()
