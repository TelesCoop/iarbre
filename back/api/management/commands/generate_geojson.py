"""Generate MVT tiles for geographic model.

This script provides a Django management command to generate MVT (Mapbox Vector Tiles)
for specified geographic models. It supports multi-threading for improved performance
and allows for the deletion of existing tiles before generating new ones.
"""
import os
import subprocess
from typing import Tuple, Type

from django.core.management import BaseCommand
from django.core.serializers import serialize
import json
from django.db.models import QuerySet, Model
from pyproj import Transformer

from api.constants import DEFAULT_ZOOM_LEVELS, GeoLevel, DataType
from api.utils.mvt_generator import MVTGenerator
from iarbre_data.models import Tile, Lcz, Vulnerability, MVTTile


class Command(BaseCommand):
    help = "Generate MVT file for a specif model."

    def add_arguments(self, parser):
        parser.add_argument(
            "--number_of_thread",
            type=int,
            default=1,
            help="Number of threads to use for generating tiles",
        )
        parser.add_argument(
            "--geolevel",
            type=str,
            required=True,
            choices=[choice for choice, _ in GeoLevel.choices],
            help=f"What geolevel to transform to MVT. Choices: {', '.join([choice for choice, _ in GeoLevel.choices])}",
        )
        parser.add_argument(
            "--datatype",
            type=str,
            required=True,
            choices=[choice for choice, _ in DataType.choices],
            help=f"What datatype to transform to MVT. Choices: {', '.join([choice for choice, _ in DataType.choices])}",
        )
        parser.add_argument(
            "--keep",
            action="store_true",
            help="Keep already existing tiles, do not delete them.",
        )

    @staticmethod
    def serialize_custom_geojson(queryset):
        """
        Serialize a queryset to GeoJSON format, replacing "fields" with custom properties.
        """
        transformer = Transformer.from_crs("EPSG:2154", "EPSG:4326", always_xy=True)
        print("Serializing JSON")
        geojson_data = json.loads(
            serialize(
                "geojson", queryset, geometry_field="map_geometry", fields=["lcz_index"]
            )
        )
        print("Adding properties to the JSON")
        for feature in geojson_data["features"]:
            polygon_coords = feature["geometry"]["coordinates"]

            transformed_coords = []
            for ring in polygon_coords:
                transformed_ring = []
                for point in ring:
                    lon, lat = transformer.transform(point[0], point[1])
                    transformed_ring.append([lon, lat])
                transformed_coords.append(transformed_ring)

            feature["geometry"]["coordinates"] = transformed_coords

            # obj = queryset.get(id=feature["id"])
            # feature["properties"] = obj.get_layer_properties()

        geojson_data["crs"] = {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
        }
        return geojson_data

    def handle(self, *args, **options):
        """Handle the command."""
        number_of_thread = options["number_of_thread"]
        geolevel = options["geolevel"]
        datatype = options["datatype"]
        if geolevel == GeoLevel.TILE.value:
            mdl = Tile
        elif geolevel == GeoLevel.LCZ.value and datatype == DataType.LCZ.value:
            mdl = Lcz
        elif (
            geolevel == GeoLevel.LCZ.value and datatype == DataType.VULNERABILITY.value
        ):
            mdl = Vulnerability
        else:
            supported_levels = [GeoLevel.TILE.value, GeoLevel.LCZ.value]
            raise ValueError(
                f"Unsupported geolevel: {geolevel}. Currently supported: {', '.join(supported_levels)}"
            )

        # if options["keep"] is False:
        #     print(f"Deleting existing MVTTile for model : {mdl._meta.model_name}.")
        #     print(
        #         MVTTile.objects.filter(
        #             geolevel=geolevel, datatype=mdl.datatype
        #         ).delete()
        #     )

        geojson_data = self.serialize_custom_geojson(mdl.objects.all())
        geojson_name = f"{geolevel}_{datatype}.geojson"
        with open(geojson_name, "w") as f:
            json.dump(geojson_data, f)
        tippecanoe_cmd = [
            "tippecanoe",
            "-o",
            f"{geolevel}_{datatype}.mbtiles",
            "--minimum-zoom",
            str(DEFAULT_ZOOM_LEVELS[0]),
            "--maximum-zoom",
            str(DEFAULT_ZOOM_LEVELS[1]),
            "-l",
            f"{geolevel}--{datatype}",
            "--force",
            "--no-tile-compression",  # Disable the default Gzip compression
            geojson_name,
        ]
        subprocess.run(tippecanoe_cmd, check=True)
        # Remove temp GeoJSON file
        breakpoint()
        os.remove(geojson_name)
