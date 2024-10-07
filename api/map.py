import math

import mapbox_vector_tile
import mercantile

from django.http import HttpResponse
from django.contrib.gis.geos import Polygon

def pixel_length(zoom):
    RADIUS = 6378137
    CIRCUM = 2 * math.pi * RADIUS
    SIZE = 512
    return CIRCUM / SIZE / 2 ** int(zoom)


def filter_instances_by_bounds(Model, bbox, zoom):
    pixel = pixel_length(zoom)
    buffer = 4 * pixel
    bbox_with_buffer = Polygon.from_bbox(
        (
            bbox["west"] - buffer,
            bbox["south"] - buffer,
            bbox["east"] + buffer,
            bbox["north"] + buffer,
        )
    )
    # Need to have a geometry field in the model with srid=3857
    return Model.objects.filter(geometry__intersects=bbox_with_buffer)


def get_bbox(x, y, zoom):
    bounds = mercantile.bounds(int(x), int(y), int(zoom))
    west, south = mercantile.xy(bounds.west, bounds.south)
    east, north = mercantile.xy(bounds.east, bounds.north)
    return {"west": west, "south": south, "east": east, "north": north}


def serialize_to_geojson_feature(instance, params):
    return {
        "geometry": instance.geometry.simplify(
            params["pixel"], preserve_topology=True
        ).wkt,
        # Need to have get_layer_properties method in the model
        "properties": instance.get_layer_properties(params),
    }

def format_to_geojson_feature_collection(division, instances, params):
    return {
        "name": division,
        "features": [
            serialize_to_geojson_feature(instance, params) for instance in instances
        ],
    }

def territories_to_tile(Model, x, y, zoom, params):
    bbox = get_bbox(x, y, zoom)
    instances = filter_instances_by_bounds(Model, bbox, zoom)

    params = {**params, "pixel": pixel_length(zoom)}

    feature_collection = format_to_geojson_feature_collection(
        Model.division, instances, params
    )
    vector_tile = mapbox_vector_tile.encode(
        feature_collection,
        quantize_bounds=(bbox["west"], bbox["south"], bbox["east"], bbox["north"]),
    )
    return HttpResponse(vector_tile, content_type="application/vnd.mapbox-vector-tile")