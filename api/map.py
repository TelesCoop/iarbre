import math
import time

import geobuf
import mercantile

from django.http import HttpResponse
from django.contrib.gis.geos import Polygon


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
        "properties": instance.get_layer_properties(),
    }


def format_to_geojson_feature_collection(name, instances, params):
    return {
        "name": name,
        "type": "FeatureCollection",
        "features": [
            serialize_to_geojson_feature(instance, params) for instance in instances
        ],
    }


def territories_to_tile(Model, x, y, zoom):
    bbox = get_bbox(x, y, zoom)
    start_time = time.time()
    instances = filter_instances_by_bounds(Model, bbox, zoom)
    end_time = time.time()
    print(f"Time to get instances: {end_time - start_time}")
    if len(instances):
        print(len(instances))

    params = {"pixel": pixel_length(zoom)}

    feature_collection = format_to_geojson_feature_collection(
        Model.type, instances, params
    )
    end_time_2 = time.time()
    print(f"Time to format instances: {end_time_2 - end_time}")
    # optimise encode
    # vector_tile = mapbox_vector_tile.encode(
    #     feature_collection,
    #     quantize_bounds=(bbox["west"], bbox["south"], bbox["east"], bbox["north"]),
    #     extents=256,
    #     y_coord_down=True,
    # )

    tiles = geobuf.encode(
        feature_collection,
        quantize_bounds=(bbox["west"], bbox["south"], bbox["east"], bbox["north"]),
        extents=256,
        y_coord_down=True,
    )
    print(f"Time to encode vector tile: {time.time() - end_time_2}")
    return HttpResponse(tiles, content_type="application/x-protobuf")
