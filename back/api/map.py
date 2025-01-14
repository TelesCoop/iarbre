import json
import math
from functools import lru_cache

import mapbox_vector_tile
import mercantile

from django.http import HttpResponse, Http404
from django.contrib.gis.geos import Polygon
from tqdm import tqdm

from iarbre_data.models import MVTTile


def pixel_length(zoom):
    RADIUS = 6378137
    CIRCUM = 2 * math.pi * RADIUS
    SIZE = 512
    return CIRCUM / SIZE / 2 ** int(zoom)


def filter_instances_by_bounds(Model, bbox, zoom):
    bbox_with_buffer = Polygon.from_bbox(
        (
            bbox["west"],
            bbox["south"],
            bbox["east"],
            bbox["north"],
        )
    )
    # Need to have a geometry field in the model with srid=3857
    return Model.objects.filter(map_geometry__intersects=bbox_with_buffer)


def get_bbox(x, y, zoom):
    bounds = mercantile.bounds(int(x), int(y), int(zoom))
    west, south = mercantile.xy(bounds.west, bounds.south)
    east, north = mercantile.xy(bounds.east, bounds.north)
    return {"west": west, "south": south, "east": east, "north": north}


def serialize_to_geojson_feature(instance, params):
    return {
        "geometry": instance.map_geometry.wkt,
        # Need to have get_layer_properties method in the model
        "properties": instance.get_layer_properties(),
    }


def format_to_geojson_feature_collection(name, instances, params):
    return {
        "name": name,
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "EPSG:3857"}},
        "features": [
            serialize_to_geojson_feature(instance, params)
            for instance in tqdm(
                instances, desc="Serializing instances", total=len(instances)
            )
        ],
    }


def territories_to_tile(Model, x, y, zoom):
    bbox = get_bbox(x, y, zoom)
    instances = filter_instances_by_bounds(Model, bbox, zoom)
    params = {"pixel": pixel_length(zoom)}

    feature_collection = format_to_geojson_feature_collection(
        Model.type, instances, params
    )

    tiles = mapbox_vector_tile.encode(
        feature_collection,
        quantize_bounds=(bbox["west"], bbox["south"], bbox["east"], bbox["north"]),
        extents=256,
        y_coord_down=True,
    )
    return HttpResponse(tiles, content_type="application/x-protobuf")


@lru_cache(maxsize=1024)
def load_tiles(model, x, y, zoom):
    try:
        tile = MVTTile.objects.get(zoom_level=zoom, tile_x=x, tile_y=y)
        return HttpResponse(tile.mvt_file, content_type="application/x-protobuf")
    except MVTTile.DoesNotExist:
        raise Http404("Tile not found")


def generate_geojson_file(instances, Model, geojson_file_path="output.geojson"):
    params = {}

    # Format the instances into a GeoJSON feature collection
    feature_collection = format_to_geojson_feature_collection(
        Model.type, instances, params
    )

    # Write the feature collection to a .geojson file
    with open(geojson_file_path, "w") as geojson_file:
        # generate compress geojson
        json.dump(feature_collection, geojson_file)
