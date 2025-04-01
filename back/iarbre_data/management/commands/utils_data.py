from itertools import islice

import numpy as np
from shapely import unary_union
from shapely.geometry import box
from functools import reduce
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.contrib.gis.geos import GEOSGeometry
import shapely
import geopandas as gpd
from tqdm import tqdm

from iarbre_data.models import Data
from iarbre_data.settings import TARGET_PROJ


def batched(iterable, n) -> None:
    """Batch data into tuples of length n. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def apply_actions(df: gpd.GeoDataFrame, actions: dict) -> gpd.GeoDataFrame:
    """
    Apply a sequence of actions to a Geometry.

    Args:
        df (GeoDataFrame): GeoDataFrame to apply actions to.
        actions (dict): Actions to apply to the GeoDataFrame.

    Returns:
        df (GeoDataFrame): GeoDataFrame with actions applied.
    """
    if actions.get("filter"):
        df = df[df[actions["filter"]["name"]] == actions["filter"]["value"]]
    if actions.get("filters"):
        df = df[
            reduce(
                lambda x, y: x | y,
                [
                    df[filter_["name"]] == filter_["value"]
                    for filter_ in actions["filters"]
                ],
            )
        ]
    if actions.get("exclude"):
        if type(actions["exclude"]["value"]) == list:
            df = df[~df[actions["exclude"]["name"]].isin(actions["exclude"]["value"])]
        else:
            df = df[df[actions["exclude"]["name"]] != actions["exclude"]["value"]]
    if actions.get("explode"):
        df = df.explode(index_parts=False)
    if actions.get("buffer_size"):
        df = df.buffer(actions["buffer_size"])
    if actions.get("buffer"):
        buffer_distances = df[actions["buffer"]["distance_column"]]
        if "_cm" in actions["buffer"]["distance_column"]:
            buffer_distances /= 100
        df = df.buffer(buffer_distances)
    if actions.get("simplify"):
        df = df.simplify(actions["simplify"])
    if actions.get("union"):
        if isinstance(df, gpd.GeoDataFrame):
            df = df["geometry"]
        geometry = unary_union(df)
        df = gpd.GeoDataFrame({"geometry": [geometry]}, crs=TARGET_PROJ)

    # Transform in Polygon
    df = df.explode(index_parts=False)
    df = df[df.geometry.type == "Polygon"]
    return df


def process_data(df: gpd.GeoDataFrame, data_config: dict) -> list:
    """
    Process geometries.

    Args:
        df (GeoDataFrame): GeoDataFrame to apply actions on.
        data_config (dict): Configuration of the data.

    Returns:
        datas (list): Processed data.
    """
    datas = []
    actions_factors = zip(
        data_config.get("actions", [{}]), data_config["factors"]
    )  # Default actions to None

    for actions, factor in actions_factors:
        sub_df = apply_actions(df.copy(), actions)
        # print(f"Breaking large geometries: {len(sub_df)}")
        # sub_df = split_factor_dataframe(sub_df, grid_size=10000)
        if len(sub_df) == 0:
            print(f"Factor: {factor} only contained Points")
            continue
        datas += [
            {"geometry": geometry, "factor": factor} for geometry in sub_df.geometry
        ]
    return datas


def save_geometries(datas: list[dict], data_config: dict) -> None:
    """
    Save geometries to the database.

    Args:
        datas (list[dict]): List of dictionaries containing geometries and metadata to save to the database.
        data_config (dict): Configuration of the data.

    Returns:
        None
    """
    for ix, batch in enumerate(tqdm(batched(datas, 1000))):
        Data.objects.bulk_create(
            [
                Data(
                    **{
                        **data,
                        "geometry": GEOSGeometry(data["geometry"].wkt),
                        "metadata": data_config["name"],
                    }
                )
                for data in batch
            ]
        )


def split_large_polygon(
    geom: shapely.geometry.Polygon, grid_size: float
) -> list[shapely.geometry.MultiPolygon]:
    """
    Split a large polygon into smaller chunks based on a grid.

    Args:
        geom (shapely.geometry.Polygon): Polygon to split.
        grid_size (float): Size of the grid in meters.

    Returns:
        list[shapely.geometry.MultiPolygon]: MultiPolygon with the split parts.
    """
    if geom is None or geom.is_empty:
        return None
    # Create a grid covering the bounding box of the geometry
    minx, miny, maxx, maxy = geom.bounds
    if (maxx - minx > grid_size) or (maxy - miny > grid_size):
        gridx = np.arange(minx, maxx, grid_size)
        if gridx[-1] != maxx:
            gridx = np.append(gridx, maxx)
        gridy = np.arange(miny, maxy, grid_size)
        if gridy[-1] != maxy:
            gridy = np.append(gridy, maxy)

        grid_cells = [
            box(x, y, x + grid_size, y + grid_size) for x in gridx for y in gridy
        ]

        clipped_parts = [
            geom.intersection(cell) for cell in grid_cells if geom.intersects(cell)
        ]
        result = [part for part in clipped_parts if not part.is_empty]
    else:
        result = [geom]
    return result


def split_factor_dataframe(
    factor_df: gpd.GeoDataFrame, grid_size: float = 10000
) -> gpd.GeoDataFrame:
    """Split Polygons of each row into smaller ones, following a grid.

    Args:
        factor_df (geopandas.GeoDataFrame): DataFrame with geometries for a factor
        grid_size (float): Size of the grid in meters that will be used to break geometries.

    Returns:
        factor_df (geopandas.GeoDataFrame): New dataframe with smaller geometries.
    """
    geometries = factor_df.geometry.values

    def split_polygon_parallel(polygon):
        """Utils"""
        return split_large_polygon(polygon, grid_size=grid_size)

    split_geom = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_polygon = {
            executor.submit(split_polygon_parallel, polygon): polygon
            for polygon in geometries
        }
        for future in as_completed(future_to_polygon):
            polygon = future_to_polygon.pop(future)
            try:
                results = future.result()
                split_geom.extend(results)
            except Exception as e:
                print(f"Error processing polygon {polygon}: {e}")
    factor_df_split = gpd.GeoDataFrame({"geometry": split_geom}, crs=factor_df.crs)
    flattened_geometries = []
    for idx, row in factor_df_split.iterrows():
        flattened_geometries.append({"geometry": row["geometry"], "original_id": idx})

    factor_df_split = gpd.GeoDataFrame(
        flattened_geometries, geometry="geometry", crs=factor_df.crs
    )
    # Some 'Point' may appear on edges of the grid, remove them
    factor_df_split = factor_df_split.explode(index_parts=False)
    factor_df_split = factor_df_split[factor_df_split.geometry.type == "Polygon"]
    return factor_df_split
