import shapely
from iarbre_data.models import City


def load_geodataframe_from_db(queryset, fields):
    """Load a GeoDataFrame from a Django model queryset.
    Params:
        queryset (QuerySet): Django queryset to load data from.
        fields (list[str]): List of fields to include in the GeoDataFrame.
    Returns:
        GeoDataFrame: GeoDataFrame with data from the queryset.
    """
    import geopandas as gpd

    df = gpd.GeoDataFrame(
        [
            dict(
                geometry=data.geometry,
                **{field: getattr(data, field) for field in fields},
            )
            for data in queryset
        ]
    )
    df.geometry = df["geometry"].apply(
        lambda el: shapely.wkt.loads(el.wkt)
    )  # Shapely used to transform string to geometry
    return df.set_geometry("geometry")


def select_city(insee_code_city):
    """Select a list of city based on INSEE_CODE.
    Params:
        insee_code_city (str): INSEE code of the city or cities to select.
    Returns:
        GeoDataFrame: GeoDataFrame containing the selected city or cities.
    """
    if insee_code_city is not None:  # Perform selection only for a city
        insee_code_city = insee_code_city.split(",")
        selected_city_qs = City.objects.filter(code__in=insee_code_city)
        if not selected_city_qs.exists():
            raise ValueError(f"No city found with INSEE code {insee_code_city}")
        selected_city = load_geodataframe_from_db(
            selected_city_qs, ["id", "name", "code"]
        )
    else:
        selected_city = load_geodataframe_from_db(
            City.objects.all(), ["id", "name", "code"]
        )
    return selected_city
