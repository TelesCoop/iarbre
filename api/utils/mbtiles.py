import os
import json
import sqlite3
import subprocess

import geopandas as gpd
from django.conf import settings
from tqdm import tqdm


class MBTilesGenerator:
    """
    Comprehensive MBTiles generation utility for Django spatial models
    """

    @classmethod
    def queryset_to_geojson(cls, queryset, output_path: str):
        """
        Convert Django spatial queryset to GeoJSON

        Args:
            queryset: Django QuerySet with spatial model instances
            output_path: Path to save GeoJSON file
        """
        features = []
        for instance in tqdm(queryset, desc="Converting queryset to GeoJSON"):
            try:
                # Ensure geometry is valid
                geom = instance.geometry.transform(4326, clone=True)

                # Convert to GeoJSON
                geojson_geom = json.loads(geom.geojson)

                feature = {
                    'type': 'Feature',
                    'geometry': geojson_geom,
                    'properties': instance.get_layer_properties()
                }
                features.append(feature)
            except Exception as e:
                print(f"Error processing instance {instance.id}: {e}")

        # Create FeatureCollection
        feature_collection = {
            'type': 'FeatureCollection',
            'features': features
        }

        # Write to GeoJSON
        with open(output_path, 'w') as f:
            json.dump(feature_collection, f)

        return output_path

    @classmethod
    def generate_mbtiles_with_tippecanoe(
            cls,
            geojson_path: str,
            output_path: str,
            layer_name: str,
            max_zoom: int = 14,
            min_zoom: int = 0
    ):
        """
        Generate MBTiles using Tippecanoe with advanced configuration

        Args:
            geojson_path: Path to input GeoJSON file
            output_path: Path to output MBTiles file
            max_zoom: Maximum zoom level
            min_zoom: Minimum zoom level
        """
        try:
            print("Generating MBTiles with Tippecanoe...")
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Tippecanoe command with advanced options
            cmd = [
                'tippecanoe',
                '-o', output_path,
                '-Z', str(min_zoom),  # Minimum zoom
                '-z', str(max_zoom),  # Maximum zoom

                # Optimization flags
                '--drop-densest-as-needed',
                '--extend-zooms-if-still-dropping',
                '--simplify-only-low-zooms',

                # Feature handling
                '--layer=spatial_data',  # Layer name in the MBTiles

                # Compression and efficiency
                '--no-tile-compression',  # Let Django/MapLibre handle compression
                '--force',  # Overwrite existing file

                # Metadata
                '--name', layer_name,
                '--description', "",

                # Input file
                geojson_path
            ]

            # Execute Tippecanoe
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            print("MBTiles generation successful")
            return output_path

        except subprocess.CalledProcessError as e:
            print(f"Tippecanoe Error: {e.stderr}")
            raise
        except Exception as e:
            print(f"MBTiles generation failed: {e}")
            raise

    @classmethod
    def geopandas_mbtiles_generation(
            cls,
            queryset,
            output_path: str,
            layer_name: str = 'spatial_layer'
    ):
        """
        Alternative MBTiles generation using GeoPandas

        Args:
            queryset: Django spatial queryset
            output_path: Path to output MBTiles
            layer_name: Name of the layer in MBTiles
        """
        # Convert queryset to GeoDataFrame
        data = list(queryset.values('id', 'geom', 'name'))
        gdf = gpd.GeoDataFrame(data)

        # Ensure proper CRS (typically EPSG:4326)
        gdf.set_crs(epsg=4326, inplace=True)

        # Write to GeoPackage (intermediate step)
        gpkg_path = output_path.replace('.mbtiles', '.gpkg')
        gdf.to_file(gpkg_path, driver='GPKG')

        # Use ogr2ogr to convert to MBTiles
        cmd = [
            'ogr2ogr',
            '-f', 'MBTiles',
            '-dsco', f'LAYER_NAME={layer_name}',
            output_path,
            gpkg_path
        ]

        subprocess.run(cmd, check=True)

        # Optional: Clean up intermediate file
        os.remove(gpkg_path)

        return output_path

    @classmethod
    def generate_mbtiles_from_model(
            cls,
            queryset,
            output_dir: str = None,
            filename: str = 'spatial_data.mbtiles',
    ):
        """
        Comprehensive method to generate MBTiles from a Django spatial model

        Args:
            queryset: Django QuerySet with spatial model instances
            output_dir: Directory to save MBTiles
            filename: Name of the output file
            filter_kwargs: Optional filtering for queryset
        """
        # Default output directory
        if output_dir is None:
            output_dir = os.path.join(settings.BASE_DIR, 'data')

        # Ensure directory exists
        os.makedirs(output_dir, exist_ok=True)


        # Temporary GeoJSON path
        geojson_path = os.path.join(output_dir, 'temp_spatial_data.geojson')
        output_path = os.path.join(output_dir, filename)

        layer_name = queryset[0].type

        try:
            # Convert to GeoJSON
            geojson_path = cls.queryset_to_geojson(queryset, geojson_path)

            # Generate MBTiles
            mbtiles_path = cls.generate_mbtiles_with_tippecanoe(
                geojson_path,
                output_path,
                layer_name
            )

            # Clean up temporary GeoJSON
            os.remove(geojson_path)

            return mbtiles_path

        except Exception as e:
            print(f"MBTiles generation failed: {e}")
            # Optional: log error or handle differently
            raise


class MBTilesHandler:
    def __init__(self, mbtiles_path):
        """
        Initialize MBTiles handler with specific tileset

        :param mbtiles_path: Full path to .mbtiles file
        """
        self.mbtiles_path = mbtiles_path

        # Validate MBTiles file exists
        if not os.path.exists(mbtiles_path):
            raise ValueError(f"MBTiles file not found: {mbtiles_path}")

        # Metadata cache
        self._metadata = None

    def get_metadata(self):
        """
        Retrieve metadata about the MBTiles tileset

        :return: Dictionary of tileset metadata
        """
        if self._metadata is not None:
            return self._metadata

        with sqlite3.connect(self.mbtiles_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, value FROM metadata")
            self._metadata = dict(cursor.fetchall())

        return self._metadata

    def get_vector_tile(self, z, x, y):
        """
        Retrieve a specific vector tile from MBTiles

        :param z: Zoom level
        :param x: X coordinate
        :param y: Y coordinate
        :return: Vector tile data or None
        """
        with sqlite3.connect(self.mbtiles_path) as conn:
            cursor = conn.cursor()

            # Flip Y coordinate (TMS to XYZ)
            flipped_y = (2 ** z - 1) - y

            cursor.execute(
                "SELECT tile_data FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?",
                (z, x, flipped_y)
            )

            result = cursor.fetchone()
            return result[0] if result else None