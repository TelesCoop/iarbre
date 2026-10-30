from collections import Counter

from django.contrib.gis.db.models import Union
import rasterio
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.core.management import BaseCommand
from rasterio.transform import from_origin
from rasterio.features import rasterize
import numpy as np
import os

from scipy import ndimage

from iarbre_data.data_config import FACTORS
from iarbre_data.models import City
from iarbre_data.settings import BASE_DIR, SRID_DB
from iarbre_data.utils.database import load_geodataframe_from_db, log_progress
from iarbre_data.utils.factor_layers import (
    Layer,
    get_factor_layers,
    get_layer_queryset,
)
from iarbre_data.utils.factor_margin import get_factor_blur, get_factor_margin


def rasterize_layer(
    layer: Layer,
    all_cities_union: GEOSGeometry,
    shape: tuple,
    transform: rasterio.Affine,
    margin: float = 0,
) -> np.ndarray:
    qs = get_layer_queryset(layer).filter(geometry__intersects=all_cities_union)
    layer_df = load_geodataframe_from_db(qs, [])
    if layer_df.empty:
        return np.zeros(shape, dtype=np.uint8)
    if margin:
        layer_df.geometry = layer_df.geometry.buffer(margin)
    return rasterize(
        layer_df.geometry,
        out_shape=shape,
        transform=transform,
        fill=0,
        default_value=1,
        dtype=np.uint8,
    )


class LayerRasterizer:
    def __init__(
        self,
        all_cities_union: GEOSGeometry,
        shape: tuple,
        transform: rasterio.Affine,
        uses: Counter | None = None,
    ):
        self.all_cities_union = all_cities_union
        self.shape = shape
        self.transform = transform
        self.uses = uses or Counter()
        self.cache = {}

    def __call__(self, layer: Layer, margin: float = 0) -> np.ndarray:
        key = (layer, margin)
        if key not in self.cache:
            raster = rasterize_layer(
                layer, self.all_cities_union, self.shape, self.transform, margin
            )
            if self.uses[key] <= 1:
                return raster
            self.cache[key] = raster
        self.uses[key] -= 1
        return self.cache[key] if self.uses[key] else self.cache.pop(key)


def rasterize_data_across_all_cities(
    factor_name: str,
    height: int,
    width: int,
    height_out: int,
    width_out: int,
    transform: rasterio.Affine,
    transform_out: rasterio.Affine,
    all_cities_union: GEOSGeometry,
    grid_size: int = 5,
    output_dir: str = None,
    allow_blank: bool = False,
    margin: float = 0,
    include: list[Layer] | None = None,
    exclude: list[Layer] | None = None,
    blur: float = 0,
    rasterizer: LayerRasterizer | None = None,
) -> None:
    """
    Convert Data polygons to a single binary raster across all cities to avoid border effects.

    This function rasterizes the geometries of a specified factor across all cities, sums the raster values
    over grid_size x grid_size blocks, and saves the resulting raster to a file.

    Args:
        factor_name (str): Name of the factor to transform to raster.
        height (int): Height of the output raster.
        width (int): Width of the output raster.
        height_out (int): Height of the output raster after aggregation.
        width_out (int): Width of the output raster after aggregation.
        transform (rasterio.Affine): Affine transformation for the factor transformation.
        transform_out (rasterio.Affine): Affine transformation for the raster output.
        all_cities_union (GEOSGeometry): GEOSGeometry containing the union of all city geometries.
        grid_size (int, optional): Size of the aggregation block in pixels. Defaults to 5.
        output_dir (str, optional): Directory to save the raster file. Defaults to None.
        allow_blank (bool, optional): Write an all-zero raster instead of raising when the factor has no data. Defaults to False.
        margin (float, optional): Buffer in meters applied to the geometries before rasterizing. Defaults to 0.
        include (list, optional): Layers whose union forms the factor. Defaults to the factor's Data rows.
        exclude (list, optional): Layers removed from the factor. Defaults to None.
        blur (float, optional): Gaussian sigma in meters for the position uncertainty. Negative factors only grow, positive ones only shrink. Defaults to 0.
        rasterizer (LayerRasterizer, optional): Rasterizes the layers, keeping those shared by several factors. Defaults to a rasterizer without cache.

    Returns:
        None
    """
    max_count = grid_size * grid_size
    os.makedirs(output_dir, exist_ok=True)

    rasterizer = rasterizer or LayerRasterizer(
        all_cities_union, (height, width), transform
    )

    log_progress(f"Rasterizing {factor_name}")
    # Rasterize the shapes
    raster = np.zeros((height, width), dtype=np.uint8)
    for layer in include or [("data", factor_name)]:
        raster |= rasterizer(layer, margin)
    for layer in exclude or []:
        raster[rasterizer(layer) > 0] = 0
    if not raster.any():
        if not allow_blank:
            raise ValueError(f"{factor_name} is producing a blank tif.")
        log_progress(f"{factor_name} is blank in this extent")
    if blur:
        blurred = ndimage.gaussian_filter(raster, blur, output=np.float32)
        pessimistic = np.maximum if FACTORS[factor_name] < 0 else np.minimum
        raster = pessimistic(blurred, raster, out=blurred)
    log_progress("Sum on 5x5")
    coarse_raster = (
        raster[: height_out * grid_size, : width_out * grid_size]
        .reshape(height_out, grid_size, width_out, grid_size)
        .sum(axis=(1, 3), dtype=np.float32)
    )
    coarse_raster *= 100 / max_count
    coarse_raster = coarse_raster.astype(np.uint8)
    # Save the raster to file
    output_path = os.path.join(output_dir, f"{factor_name}.tif")
    log_progress(f"Saving {factor_name}")
    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=height_out,
        width=width_out,
        count=1,
        dtype=np.uint8,
        crs="EPSG:2154",
        transform=transform_out,
    ) as dst:
        dst.write(coarse_raster, 1)


class Command(BaseCommand):
    help = "Convert Data polygons to raster."

    def add_arguments(self, parser):
        """Add arguments to the command."""
        parser.add_argument(
            "--grid-size", type=int, default=5, help="Grid size in meters"
        )
        parser.add_argument(
            "--bbox",
            type=float,
            nargs=4,
            metavar=("MINX", "MINY", "MAXX", "MAXY"),
            help="Only rasterize this extent (EPSG:2154)",
        )
        parser.add_argument(
            "--output-dir",
            default=str(BASE_DIR) + "/media/rasters/",
            help="Directory to save the rasters",
        )

    def handle(self, *args, **options):
        output_dir = options["output_dir"]
        bbox = options["bbox"]
        resolution = 1
        grid_size = options["grid_size"]
        kernel_size = grid_size / resolution
        if not kernel_size.is_integer():
            raise ValueError(
                f"Grid size should be a multiple of the resolution: {resolution}m"
            )
        kernel_size = int(kernel_size)
        if bbox:
            all_cities_union = Polygon.from_bbox(bbox)
            all_cities_union.srid = SRID_DB
        else:
            # remove test data
            all_cities_union = City.objects.exclude(code="38250").aggregate(
                union=Union("geometry")
            )["union"]
        minx, miny, maxx, maxy = all_cities_union.extent

        width = int((maxx - minx) / resolution)
        height = int((maxy - miny) / resolution)
        transform = from_origin(minx, maxy, resolution, resolution)

        width_out = int((maxx - minx) / grid_size)
        height_out = int((maxy - miny) / grid_size)
        transform_out = from_origin(minx, maxy, grid_size, grid_size)

        factor_options = {}
        layer_uses = Counter()
        for factor_name in FACTORS.keys():
            if factor_name == "QPV":
                continue
            include, exclude = get_factor_layers(factor_name, grid_size)
            margin = get_factor_margin(factor_name, grid_size)
            factor_options[factor_name] = dict(
                margin=margin,
                include=include,
                exclude=exclude,
                blur=get_factor_blur(factor_name, grid_size),
            )
            layer_uses.update((layer, margin) for layer in include)
            layer_uses.update((layer, 0) for layer in exclude)
        rasterizer = LayerRasterizer(
            all_cities_union, (height, width), transform, layer_uses
        )

        for factor_name, factor_kwargs in factor_options.items():
            log_progress(f"Processing {factor_name}")
            rasterize_data_across_all_cities(
                factor_name,
                height,
                width,
                height_out,
                width_out,
                transform,
                transform_out,
                all_cities_union=all_cities_union,
                grid_size=kernel_size,
                output_dir=output_dir,
                allow_blank=bool(bbox),
                rasterizer=rasterizer,
                **factor_kwargs,
            )
