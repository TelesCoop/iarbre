from pathlib import Path
from django.core.management.base import BaseCommand
from argparse import RawTextHelpFormatter

# gdal requires specific installation
# and version depending on your Linux Installation
# You probably have GDAL already installed
# Just check which is one is on your global python env
# and install it in your localenv
# You can get the version with ogrinfo --version
from osgeo import gdal, ogr, osr


class Command(BaseCommand):
    help = """Vectorize a raster map (.tiff) into a vector one (.shp) using gdal
    python3 manage.py vectorize_raster -i final_fused.tif -o final_fused.gpkg
    python3 manage.py vectorize_raster -i final_fused.tif -o final_fused.shp -f "ESRI Shapefile"
    python3 manage.py vectorize_raster -i final_fused.tif -o final_fused.geojson -f GeoJSON --8connected

    """

    def create_parser(self, prog_name, subcommand, **kwargs):
        return super().create_parser(
            prog_name, subcommand, **kwargs, formatter_class=RawTextHelpFormatter
        )

    def add_arguments(self, parser):
        parser.add_argument(
            "-i",
            "--input",
            type=str,
            required=True,
            help="Input raster file (TIF)",
        )

        parser.add_argument(
            "-o",
            "--output",
            type=str,
            required=True,
            help="Output vector file (extension determines format if --format not specified)",
        )

        parser.add_argument(
            "-f",
            "--format",
            choices=["ESRI Shapefile", "GPKG", "GeoJSON"],
            default=None,
            help="Vector format (default: auto-detect from output extension)",
        )

        parser.add_argument(
            "--field-name",
            type=str,
            default="class",
            help="Name of the field to store pixel values (default: class)",
        )

        parser.add_argument(
            "--8connected",
            dest="use_8connected",
            action="store_true",
            help="Use 8-connectedness for polygonization (treats diagonal pixels as connected)",
        )

    @staticmethod
    def vectorize_raster(
        raster_path,
        vector_path,
        vector_format="GPKG",
        use_8connected=False,
        field_name="class",
    ):
        print(f"\n{'=' * 70}")
        print(f"Vectorizing: {raster_path} -> {vector_path}")
        print(f"Format: {vector_format}, 8-connected: {use_8connected}")
        print(f"{'=' * 70}\n")

        src_ds = gdal.Open(str(raster_path))
        if src_ds is None:
            print(f"✗ Error: Could not open raster: {raster_path}")
            return False

        src_band = src_ds.GetRasterBand(1)

        driver_name = (
            vector_format if vector_format != "ESRI Shapefile" else "ESRI Shapefile"
        )
        drv = ogr.GetDriverByName(driver_name)
        if drv is None:
            print(f"✗ Error: Could not get driver: {driver_name}")
            return False

        if Path(vector_path).exists():
            drv.DeleteDataSource(str(vector_path))

        dst_ds = drv.CreateDataSource(str(vector_path))
        if dst_ds is None:
            print(f"✗ Error: Could not create vector file: {vector_path}")
            return False

        srs = None
        if src_ds.GetProjection():
            srs = osr.SpatialReference()
            srs.ImportFromWkt(src_ds.GetProjection())

        dst_layer = dst_ds.CreateLayer("vegetation", srs=srs)
        field_defn = ogr.FieldDefn(field_name, ogr.OFTInteger)
        dst_layer.CreateField(field_defn)

        options = []
        if use_8connected:
            options.append("8CONNECTED=8")

        gdal.Polygonize(
            src_band, None, dst_layer, 0, options, callback=gdal.TermProgress
        )

        dst_ds = None
        src_ds = None

        print(f"\n✓ Vectorization complete: {vector_path}")
        return True

    def handle(self, *args, **options):
        input_path = Path(options["input"])
        if not input_path.exists():
            print(f"✗ Error: Input raster not found: {input_path}")
            return 1

        vector_format = options["format"]
        if vector_format is None:
            ext = Path(options["output"]).suffix.lower()
            ext_to_format = {
                ".shp": "ESRI Shapefile",
                ".gpkg": "GPKG",
                ".geojson": "GeoJSON",
            }
            vector_format = ext_to_format.get(ext, "GPKG")
            print(f"Auto-detected format: {vector_format}")

        success = self.vectorize_raster(
            options["input"],
            options["output"],
            vector_format=vector_format,
            use_8connected=options["use_8connected"],
            field_name=options["field_name"],
        )

        return 0 if success else 1
