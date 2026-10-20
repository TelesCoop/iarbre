import geopandas as gpd
from django.test import TestCase
from shapely.geometry import box

from iarbre_data.management.commands.import_public_buildings import (
    build_public_buildings,
    filter_public_buildings,
)
from iarbre_data.models import PublicBuilding
from iarbre_data.settings import SRID_DB


def bdtopo_row(toponyme, categorie, nature, geometry, uai=None, fictif=False):
    return {
        "cleabs": toponyme,
        "categorie": categorie,
        "nature": nature,
        "nature_detaillee": None,
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

        self.assertEqual(list(filtered.toponyme), ["Mairie du 1er arrondissement"])

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
                    "Musée des Beaux-Arts",
                    "Culture et loisirs",
                    "Musée",
                    box(842300, 6520100, 842305, 6520105),
                    fictif=True,
                ),
            ],
            crs=SRID_DB,
        )

        buildings = {b.name: b for b in build_public_buildings(gdf, directory)}

        self.assertNotIn("Institution des Chartreux", buildings)
        school = buildings["École Élémentaire Victor Hugo"]
        self.assertEqual(school.category, PublicBuilding.Category.ENSEIGNEMENT)
        self.assertEqual(school.student_count, 338)
        self.assertEqual(school.geometry.geom_type, "Polygon")
        museum = buildings["Musée des Beaux-Arts"]
        self.assertEqual(museum.category, PublicBuilding.Category.CULTURE)
        self.assertEqual(museum.geometry.geom_type, "Point")
