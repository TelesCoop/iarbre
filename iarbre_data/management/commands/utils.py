import shapely


def load_geodataframe_from_db(queryset, fields):
    """
    Load a GeoDataFrame from a Django model queryset.
    """
    import geopandas as gpd

    df = gpd.GeoDataFrame(
        [
            dict(
                geometry=data.geometry,
                **{field: getattr(data, field) for field in fields}
            )
            for data in queryset
        ]
    )
    df.geometry = df["geometry"].apply(
        lambda el: shapely.wkt.loads(el.wkt)
    )  # Shapely used to transform string to geometry
    return df.set_geometry("geometry")


def transform_geometry_to_srid_and_simplify(geometry, tolerance=0.1):
    """
    Transform a geometry to a new SRID and simplify it.
    """
    geometry = geometry.transform(3857, clone=True)

    # reduce the number of decimals to avoid too much precision and return a simplified geometry
    return geometry.simplify(tolerance=tolerance)
