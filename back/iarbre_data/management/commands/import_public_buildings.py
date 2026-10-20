import re

import geopandas as gpd
import pandas as pd
from django.contrib.gis.geos import GEOSGeometry
from django.core.management import BaseCommand
from django.db import transaction

from iarbre_data.data_config import PUBLIC_BUILDINGS
from iarbre_data.models import PublicBuilding
from iarbre_data.settings import SRID_DB
from iarbre_data.utils.database import select_city
from iarbre_data.utils.download import download_dbtopo, download_from_url

UAI_PATTERN = re.compile(r"MEN:(\w{8})")


def to_bool(value) -> bool:
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value) if pd.notna(value) else False


def extract_uai(identifiants_sources) -> str | None:
    if not isinstance(identifiants_sources, str):
        return None
    match = UAI_PATTERN.search(identifiants_sources)
    return match.group(1).upper() if match else None


def load_education_directory() -> dict[str, dict]:
    """Map UAI to status, student count and priority education network from Grand Lyon."""
    frames = [
        download_from_url(PUBLIC_BUILDINGS["grandlyon_url"], layer)
        for layer in PUBLIC_BUILDINGS["grandlyon_edu_layers"]
    ]
    directory = {}
    for frame in frames:
        for row in frame.itertuples():
            student_count = getattr(row, "nombre_d_eleves", None)
            priority = getattr(row, "appartenance_education_prioritaire", None)
            directory[str(row.uai).upper()] = {
                "status": getattr(row, "statut_public_prive", None),
                "student_count": (
                    int(student_count) if pd.notna(student_count) else None
                ),
                "education_priority": priority if pd.notna(priority) else None,
            }
    return directory


def filter_public_buildings(gdf: gpd.GeoDataFrame, cities_geometry) -> gpd.GeoDataFrame:
    gdf = gdf.drop_duplicates(subset="cleabs")
    gdf = gdf[gdf["categorie"].isin(PUBLIC_BUILDINGS["categories"].keys())]
    gdf = gdf[~gdf["nature"].isin(PUBLIC_BUILDINGS["excluded_natures"])]
    gdf = gdf[gdf["etat_de_l_objet"] == PUBLIC_BUILDINGS["state_in_service"]]
    gdf = gdf[gdf.geometry.notna() & gdf.geometry.is_valid]
    return gdf[gdf.geometry.representative_point().within(cities_geometry)]


def build_public_buildings(
    gdf: gpd.GeoDataFrame, directory: dict[str, dict]
) -> list[PublicBuilding]:
    buildings = []
    for row in gdf.itertuples():
        uai = extract_uai(row.identifiants_sources)
        school = directory.get(uai, {}) if uai else {}
        if school.get("status") == "Privé":
            continue
        fictif = to_bool(row.fictif)
        geometry = row.geometry.centroid if fictif else row.geometry
        buildings.append(
            PublicBuilding(
                geometry=GEOSGeometry(geometry.wkt, srid=SRID_DB),
                cleabs=row.cleabs,
                category=PUBLIC_BUILDINGS["categories"][row.categorie],
                nature=row.nature,
                nature_detaillee=(
                    row.nature_detaillee if pd.notna(row.nature_detaillee) else None
                ),
                name=row.toponyme if pd.notna(row.toponyme) else None,
                uai=uai,
                fictif=fictif,
                insee_commune=(
                    row.insee_commune if pd.notna(row.insee_commune) else None
                ),
                student_count=school.get("student_count"),
                education_priority=school.get("education_priority"),
            )
        )
    return buildings


class Command(BaseCommand):
    help = "Import public buildings from IGN BD TOPO, excluding private schools"

    def handle(self, *args, **options):
        gdf = download_dbtopo(
            PUBLIC_BUILDINGS["bdtopo_url"],
            typename=PUBLIC_BUILDINGS["bdtopo_typename"],
            cache_name="public_buildings",
            columns=PUBLIC_BUILDINGS["bdtopo_columns"],
        ).to_crs(SRID_DB)
        cities_geometry = select_city(None).to_crs(SRID_DB).union_all()
        gdf = filter_public_buildings(gdf, cities_geometry)
        buildings = build_public_buildings(gdf, load_education_directory())

        with transaction.atomic():
            PublicBuilding.objects.all().delete()
            PublicBuilding.objects.bulk_create(buildings, batch_size=1000)

        self.stdout.write(
            self.style.SUCCESS(f"Imported {len(buildings)} public buildings")
        )
