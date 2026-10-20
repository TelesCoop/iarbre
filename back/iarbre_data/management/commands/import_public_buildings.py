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


def load_public_creches(cities_geometry) -> gpd.GeoDataFrame:
    """Load public crèches from Grand Lyon as point features shaped like BD TOPO ones."""
    creches = download_from_url(
        PUBLIC_BUILDINGS["grandlyon_url"], PUBLIC_BUILDINGS["grandlyon_creche_layer"]
    ).to_crs(SRID_DB)
    creches = creches[
        creches["categorie"].isin(PUBLIC_BUILDINGS["creche_public_managers"])
        & creches.geometry.within(cities_geometry)
    ]
    return gpd.GeoDataFrame(
        {
            "cleabs": "CRECHE" + creches["gid"].astype(str),
            "categorie": "Petite enfance",
            "nature": "Crèche",
            "nature_detaillee": None,
            "toponyme": creches["nom"],
            "fictif": True,
            "uai": None,
            "insee_commune": creches["insee"].astype(str),
            "capacity": creches["capacite"],
        },
        geometry=creches.geometry,
        crs=SRID_DB,
    )


def is_kept_nature(categorie: str, nature: str, nature_detaillee) -> bool:
    if nature_detaillee in PUBLIC_BUILDINGS["dropped_nature_details"]:
        return False
    kept_natures = PUBLIC_BUILDINGS["kept_natures"].get(categorie)
    if kept_natures is None:
        return True
    if nature not in kept_natures:
        return False
    kept_details = kept_natures[nature]
    return kept_details is None or nature_detaillee in kept_details


def filter_public_buildings(gdf: gpd.GeoDataFrame, cities_geometry) -> gpd.GeoDataFrame:
    gdf = gdf.drop_duplicates(subset="cleabs")
    gdf = gdf[gdf["categorie"].isin(PUBLIC_BUILDINGS["categories"].keys())]
    gdf = gdf[
        [
            is_kept_nature(row.categorie, row.nature, row.nature_detaillee)
            for row in gdf.itertuples()
        ]
    ]
    gdf = gdf[gdf["etat_de_l_objet"] == PUBLIC_BUILDINGS["state_in_service"]]
    gdf = gdf[gdf.geometry.notna() & gdf.geometry.is_valid]
    return gdf[gdf.geometry.representative_point().within(cities_geometry)]


def exclude_private_schools(
    gdf: gpd.GeoDataFrame, directory: dict[str, dict]
) -> gpd.GeoDataFrame:
    gdf = gdf.assign(uai=gdf["identifiants_sources"].map(extract_uai))
    is_private = gdf["uai"].map(
        lambda uai: directory.get(uai, {}).get("status") == "Privé"
    )
    return gdf[~is_private]


def drop_points_within_footprints(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Drop fictive footprints, shown as points, that fall inside a real footprint."""
    gdf = gdf.assign(fictif=gdf["fictif"].map(to_bool))
    points = gdf[gdf["fictif"]].set_geometry(gdf[gdf["fictif"]].geometry.centroid)
    footprints = gdf[~gdf["fictif"]]
    inside = gpd.sjoin(
        points[["geometry"]], footprints[["geometry"]], predicate="within"
    ).index
    return gdf.drop(index=inside.unique())


def drop_nested_footprints(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Drop real footprints lying inside a larger footprint, keeping one of identical ones."""
    footprints = gdf[~gdf["fictif"]][["geometry"]]
    pairs = gpd.sjoin(footprints, footprints, predicate="intersects")
    pairs = pairs[pairs.index != pairs["index_right"]]
    outer = footprints.geometry.loc[pairs["index_right"]].set_axis(pairs.index)
    inner_area = pairs.geometry.area
    outer_area = outer.area
    covered = pairs.geometry.intersection(outer, align=False).area / inner_area
    is_nested = (covered >= PUBLIC_BUILDINGS["nested_footprint_ratio"]) & (
        (inner_area < outer_area)
        | ((inner_area == outer_area) & (pairs.index > pairs["index_right"]))
    )
    return gdf.drop(index=pairs.index[is_nested].unique())


def build_public_buildings(
    gdf: gpd.GeoDataFrame, directory: dict[str, dict]
) -> list[PublicBuilding]:
    buildings = []
    for row in gdf.itertuples():
        uai = row.uai
        school = directory.get(uai, {}) if uai else {}
        fictif = row.fictif
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
                capacity=(
                    int(row.capacity)
                    if pd.notna(getattr(row, "capacity", None))
                    else None
                ),
            )
        )
    return buildings


class Command(BaseCommand):
    help = "Import public buildings from IGN BD TOPO and public crèches from Grand Lyon"

    def handle(self, *args, **options):
        gdf = download_dbtopo(
            PUBLIC_BUILDINGS["bdtopo_url"],
            typename=PUBLIC_BUILDINGS["bdtopo_typename"],
            cache_name="public_buildings",
            columns=PUBLIC_BUILDINGS["bdtopo_columns"],
        ).to_crs(SRID_DB)
        cities_geometry = select_city(None).to_crs(SRID_DB).union_all()
        directory = load_education_directory()
        gdf = filter_public_buildings(gdf, cities_geometry)
        gdf = exclude_private_schools(gdf, directory)
        gdf = pd.concat([gdf, load_public_creches(cities_geometry)], ignore_index=True)
        gdf = drop_points_within_footprints(gdf)
        gdf = drop_nested_footprints(gdf)
        buildings = build_public_buildings(gdf, directory)

        with transaction.atomic():
            PublicBuilding.objects.all().delete()
            PublicBuilding.objects.bulk_create(buildings, batch_size=1000)

        self.stdout.write(
            self.style.SUCCESS(f"Imported {len(buildings)} public buildings")
        )
