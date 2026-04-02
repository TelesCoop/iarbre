import math

EARTH_CIRCUMFERENCE = 20037508.34


def tile_to_bbox(z, x, y):
    """Convert XYZ tile coordinates to EPSG:3857 bounding box.

    Returns (x_min, y_min, x_max, y_max) in Web Mercator meters.
    """
    n = 2**z
    x_min = x / n * 360.0 - 180.0
    x_max = (x + 1) / n * 360.0 - 180.0

    y_min_lat = math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n)))
    y_max_lat = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))

    x_min_m = x_min * EARTH_CIRCUMFERENCE / 180.0
    x_max_m = x_max * EARTH_CIRCUMFERENCE / 180.0
    y_min_m = (
        math.log(math.tan((90 + math.degrees(y_min_lat)) * math.pi / 360.0))
        / math.pi
        * EARTH_CIRCUMFERENCE
    )
    y_max_m = (
        math.log(math.tan((90 + math.degrees(y_max_lat)) * math.pi / 360.0))
        / math.pi
        * EARTH_CIRCUMFERENCE
    )

    return x_min_m, y_min_m, x_max_m, y_max_m
