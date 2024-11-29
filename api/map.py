import math
import time

import mapbox_vector_tile
import mercantile
from django.contrib.gis.gdal import SpatialReference, Point, CoordTransform

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
    return Model.objects.filter(geometry__intersects=bbox_with_buffer)

def convert_bounding_box_to_wanted_srid(
        bbox, current_srid, wanted_srid
):
    source_srs = SpatialReference(current_srid)  # WGS 84
    target_srs = SpatialReference(wanted_srid)  # NAD83 / Conus Albers

    coord_transform = CoordTransform(source_srs, target_srs)

    sw_point = Point(bbox["west"], bbox["south"], srid=current_srid)
    ne_point = Point(bbox["east"], bbox["north"], srid=current_srid)

    sw_point.transform(coord_transform)
    ne_point.transform(coord_transform)

    return {
        "west": sw_point.x,
        "south": sw_point.y,
        "east": ne_point.x,
        "north": ne_point.y,
    }


def get_bbox(x, y, zoom):
    bounds = mercantile.bounds(int(x), int(y), int(zoom))
    west, south = mercantile.xy(bounds.west, bounds.south)
    east, north = mercantile.xy(bounds.east, bounds.north)

    bbox = {"west": west, "south": south, "east": east, "north": north}
    return convert_bounding_box_to_wanted_srid(
        bbox, 3857, 2154
    )


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

    tiles = mapbox_vector_tile.encode(
        feature_collection,
        quantize_bounds=(bbox["west"], bbox["south"], bbox["east"], bbox["north"]),
        extents=256,
        y_coord_down=True,
    )
    print(f"Time to encode vector tile: {time.time() - end_time_2}")
    return HttpResponse(tiles, content_type="application/x-protobuf")
