from unittest.mock import patch

import geopandas as gpd
from django.test import TestCase
from shapely.geometry import Point, box

from iarbre_data.management.commands.import_public_buildings import (
    build_public_buildings,
    drop_points_within_footprints,
    exclude_private_schools,
    filter_public_buildings,
    load_public_creches,
)
from iarbre_data.models import PublicBuilding
from iarbre_data.settings import SRID_DB


def bdtopo_row(
    toponyme,
    categorie,
    nature,
    geometry,
    uai=None,
    fictif=False,
    nature_detaillee=None,
):
    return {
        "cleabs": toponyme,
        "categorie": categorie,
        "nature": nature,
        "nature_detaillee": nature_detaillee,
        "toponyme": toponyme,
        "fictif": fictif,
        "etat_de_l_objet": "En service",
        "identifiants_sources": f"MEN:{uai}" if uai else None,
        "insee_commune": "69381",
        "geometry": geometry,
    }


class ImportPublicBuildingsCommandTest(TestCase):
    def test_filter_public_buildings(self):
        lyon_1 = box(841500, 6519500, 843500, 6521000)
        gdf = gpd.GeoDataFrame(
            [
                bdtopo_row(
                    "Mairie du 1er arrondissement",
                    "Administratif ou militaire",
                    "Mairie",
                    box(842000, 6520000, 842050, 6520050),
                ),
                bdtopo_row(
                    "Place des Terreaux",
                    "Culture et loisirs",
                    "Espace public",
                    box(842200, 6520200, 842300, 6520300),
                ),
                bdtopo_row(
                    "Bibliothèque du 1er arrondissement",
                    "Culture et loisirs",
                    "Centre de documentation",
                    box(842100, 6520100, 842130, 6520130),
                    nature_detaillee="Bibliothèque",
                ),
                bdtopo_row(
                    "Crèche Municipale de Saint-Rambert",
                    "Science et enseignement",
                    "Autre établissement d'enseignement",
                    box(842100, 6520200, 842105, 6520205),
                    nature_detaillee="Crèche",
                ),
                bdtopo_row(
                    "Opéra de Lyon",
                    "Culture et loisirs",
                    "Salle de spectacle ou conférence",
                    box(842150, 6520150, 842180, 6520180),
                ),
                bdtopo_row(
                    "Gymnase Jean Jaurès",
                    "Sport",
                    "Complexe sportif couvert",
                    box(842300, 6520300, 842350, 6520350),
                ),
                bdtopo_row(
                    "Halle de la Martinière",
                    "Industriel et commercial",
                    "Marché",
                    box(842400, 6520400, 842450, 6520450),
                ),
                bdtopo_row(
                    "Mairie du 4e arrondissement",
                    "Administratif ou militaire",
                    "Mairie",
                    box(842000, 6522000, 842050, 6522050),
                ),
            ],
            crs=SRID_DB,
        )

        filtered = filter_public_buildings(gdf, lyon_1)

        self.assertEqual(
            list(filtered.toponyme),
            ["Mairie du 1er arrondissement", "Bibliothèque du 1er arrondissement"],
        )

    def test_build_public_buildings(self):
        directory = {
            "0691300N": {
                "status": "Public",
                "student_count": 338,
                "education_priority": None,
            },
            "0693607W": {
                "status": "Privé",
                "student_count": 404,
                "education_priority": None,
            },
        }
        gdf = gpd.GeoDataFrame(
            [
                bdtopo_row(
                    "École Élémentaire Victor Hugo",
                    "Science et enseignement",
                    "Enseignement primaire",
                    box(842000, 6520000, 842080, 6520060),
                    uai="0691300N",
                ),
                bdtopo_row(
                    "Institution des Chartreux",
                    "Science et enseignement",
                    "Enseignement primaire",
                    box(841800, 6520300, 841805, 6520305),
                    uai="0693607W",
                    fictif=True,
                ),
                bdtopo_row(
                    "École Maternelle Victor Hugo",
                    "Science et enseignement",
                    "Enseignement primaire",
                    box(842030, 6520020, 842035, 6520025),
                    fictif=True,
                ),
                bdtopo_row(
                    "Musée des Beaux-Arts",
                    "Culture et loisirs",
                    "Musée",
                    box(842300, 6520100, 842305, 6520105),
                    fictif=True,
                ),
            ],
            crs=SRID_DB,
        )

        gdf = exclude_private_schools(gdf, directory)
        gdf = drop_points_within_footprints(gdf)
        buildings = {b.name: b for b in build_public_buildings(gdf, directory)}

        self.assertNotIn("Institution des Chartreux", buildings)
        self.assertNotIn("École Maternelle Victor Hugo", buildings)
        school = buildings["École Élémentaire Victor Hugo"]
        self.assertEqual(school.category, PublicBuilding.Category.ENSEIGNEMENT)
        self.assertEqual(school.student_count, 338)
        self.assertEqual(school.geometry.geom_type, "Polygon")
        museum = buildings["Musée des Beaux-Arts"]
        self.assertEqual(museum.category, PublicBuilding.Category.CULTURE)
        self.assertEqual(museum.geometry.geom_type, "Point")

    @patch("iarbre_data.management.commands.import_public_buildings.download_from_url")
    def test_load_public_creches(self, mock_download):
        lyon_1 = box(841500, 6519500, 843500, 6521000)
        mock_download.return_value = gpd.GeoDataFrame(
            {
                "nom": ["Arc En Ciel", "Les Petits Futés", "Clair De Lune"],
                "categorie": [
                    "Collectivité Locale",
                    "Association",
                    "Collectivité Locale",
                ],
                "capacite": [16, 28, 70],
                "insee": ["69381", "69381", "69003"],
                "gid": [2, 1, 3],
            },
            geometry=[
                Point(842200, 6520200),
                Point(842300, 6520300),
                Point(845000, 6530000),
            ],
            crs=SRID_DB,
        )

        creches = load_public_creches(lyon_1)

        self.assertEqual(list(creches.toponyme), ["Arc En Ciel"])
        self.assertEqual(list(creches.capacity), [16])
        self.assertTrue(creches.fictif.all())

        (creche,) = build_public_buildings(creches, {})
        self.assertEqual(creche.category, PublicBuilding.Category.PETITE_ENFANCE)
        self.assertEqual(creche.capacity, 16)
        self.assertEqual(creche.geometry.geom_type, "Point")
