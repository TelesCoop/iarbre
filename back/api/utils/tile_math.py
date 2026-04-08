import mercantile


def tile_to_bbox(z, x, y):
    """Convert XYZ tile coordinates to an EPSG:3857 bounding box.

    Returns (x_min, y_min, x_max, y_max) in Web Mercator meters.
    """
    bounds = mercantile.xy_bounds(mercantile.Tile(x, y, z))
    return bounds.left, bounds.bottom, bounds.right, bounds.top
