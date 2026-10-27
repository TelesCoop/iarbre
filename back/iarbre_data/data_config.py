# Plantability factor.
# The higher, the more plantable it is
# For example, it's easier to plant a tree on wasteland
# than at an airport
FACTORS = {
    "Souches ou emplacements libres": 3,
    "Arbres": 1,
    "Aerodrome": -5,
    "Parkings": -2,
    "Entrée parking": -5,
    "Signalisation tricolore et lumineuse matériel": -2,
    "Station velov": -1,
    "Arrêts transport en commun": -2,
    "Proximité façade": -2,
    "Bâtiments": -5,
    "Friches": 2,
    "Assainissement": -1,
    "Parcs et jardins publics": 2,
    "Giratoires": 2,
    "Espaces jeux et pietonnier": 1,
    "Friche naturelle": 3,
    "Réseau Fibre": 2,
    "Marchés forains": 1,
    "Pistes cyclable": -1,
    "Plan eau": -5,  # -3
    "Ponts": -5,
    "Réseau de chaleur urbain": -3,
    "Voies ferrées": -5,  # -2
    "Strate arborée": 1,
    "Strate basse et pelouse": 3,
    "Espaces agricoles": 1,
    "Forêts": 1,
    "Espaces artificialisés": -2,
    "Tracé de métro": -2,
    "Tracé de tramway": -2,
    "Tracé de bus": -1,
    "Rsx gaz": -3,
    "Rsx souterrains ERDF": -1,
    "Rsx aériens ERDF": -2,
    "PMR": -4,
    "Auto-partage": -2,
    "QPV": 0,
}

BLOCKING_SCORE = float(min(FACTORS.values()))

VEGESTRATE_LAYERS = [
    ("vegestrate", "arborescent"),
    ("vegestrate", "arbustif"),
    ("vegestrate", "herbacee"),
]

FINE_GRID_FACTORS = {
    "Strate arborée": {"include": [("vegestrate", "arborescent")], "uncertainty": 0.5},
    "Strate basse et pelouse": {
        "include": [
            ("vegestrate", "arbustif"),
            ("vegestrate", "herbacee"),
            ("data", "EVA sols nus, friches et milieux herbeux"),
        ],
        "exclude": [("vegestrate", "arborescent")],
        "uncertainty": 0.5,
    },
    "Espaces agricoles": {
        "include": [("data", "EVA espaces agricoles")],
        "exclude": VEGESTRATE_LAYERS,
        "uncertainty": None,
    },
    "Forêts": {
        "include": [("data", "EVA forêts")],
        "exclude": VEGESTRATE_LAYERS,
        "uncertainty": None,
    },
    "Espaces artificialisés": {
        "include": [("data", "EVA espaces artificialisés")],
        "exclude": VEGESTRATE_LAYERS,
        "uncertainty": None,
    },
}

META_FACTORS_MAPPING = {
    "Réseaux et infrastructures": [
        "Assainissement",
        "Réseau Fibre",
        "Réseau de chaleur urbain",
        "Rsx gaz",
        "Rsx souterrains ERDF",
        "Rsx aériens ERDF",
    ],
    "Infrastructure de transport": [
        "Aerodrome",
        "Parkings",
        "Entrée parking",
        "Signalisation tricolore et lumineuse matériel",
        "Station velov",
        "Arrêts transport en commun",
        "Pistes cyclable",
        "Ponts",
        "Voies ferrées",
        "Tracé de métro",
        "Tracé de tramway",
        "Tracé de bus",
        "PMR",
        "Auto-partage",
    ],
    "Bâtiments": ["Proximité façade", "Bâtiments"],
    "Espaces verts": [
        "Souches ou emplacements libres",
        "Arbres",
        "Parcs et jardins publics",
        "Friche naturelle",
        "Strate arborée",
        "Strate basse et pelouse",
        "Espaces agricoles",
        "Forêts",
    ],
    "Aménagements urbains": [
        "Giratoires",
        "Espaces jeux et pietonnier",
        "Friches",
        "Marchés forains",
    ],
    "Plan d'eau": ["Plan eau"],
    "Espaces artificialisés": ["Espaces artificialisés"],
}


UPDATES = [
    {
        "name": "Réseau Fibre",
        "file": "voirie.gpkg",
        "layer_name": "pub_app_patrimoinevoirie.liengeniecivil",
        "actions": [
            {"buffer_size": 2, "union": True},
        ],
        "factors": ["Fibre"],
        "output_type": "POINT",
    },
]

EVA_AGRICULTURAL_CODES = [211, 212, 213, 214, 215, 221, 222, 223, 224, 225, 231, 241]
EVA_FOREST_CODES = [311, 312, 322, 331, 341, 342, 351, 371, 372, 374, 411, 412]
EVA_OPEN_GROUND_CODES = [14, 16, 17, 361, 362]
EVA_ARTIFICIAL_CODES = [15]
EVA_LAND_COVER_CODES = [
    EVA_OPEN_GROUND_CODES,
    EVA_AGRICULTURAL_CODES,
    EVA_FOREST_CODES,
    EVA_ARTIFICIAL_CODES,
]


def eva_actions(code_groups: list[list[int]], **extra) -> list[dict]:
    return [
        {
            "filters": [{"name": "gl_2015", "value": code} for code in codes],
            "explode": True,
            **extra,
        }
        for codes in code_groups
    ]


DATA_FILES = [
    {
        "name": "Parkings surfacique",
        "uncertainty": 1,
        "file": "parkingsurfacique.geojson",
        "scripts": None,
        "factors": ["Parkings"],
        "output_type": "POLYGON",
    },
    {
        "name": "SLT",
        "uncertainty": 0.5,
        "file": "voirie.gpkg",
        "scripts": ["slt.py"],
        "layer_name": "pub_patrimoinevoirie.sltmateriel",
        "actions": [
            {"buffer_size": 2, "union": True},
        ],
        "factors": ["Signalisation tricolore et lumineuse matériel"],
        "output_type": "POINT",
    },
    {
        "name": "Assainissement",
        "uncertainty": None,
        "file": "assainissement.geojson",
        "scripts": ["assainissement.py"],
        "actions": [{"buffer_size": 1, "explode": True, "union": True}],
        "factors": ["Assainissement"],
        "output_type": "MULTILINESTRING",
    },
    {
        "name": "Espaces publics",
        "uncertainty": 0.5,
        "file": "espacepublic2025.geojson",
        "actions": [
            {
                "filter": {
                    "name": "typeespacepublic",
                    "value": "Parc / jardin public / square",
                }
            },
            {
                "filter": {
                    "name": "typeespacepublic",
                    "value": "Giratoire",
                }
            },
            {
                "filters": [
                    {
                        "name": "typeespacepublic",
                        "value": "Aire de jeux",
                    },
                    {
                        "name": "typeespacepublic",
                        "value": "Espace piétonnier",
                    },
                ]
            },
            {
                "filter": {
                    "name": "typeespacepublic",
                    "value": "Délaissé / Ilot végétalisé",
                }
            },
        ],
        "scripts": ["parc.py", "giratoire.py", "jeux.py" "friche_nat.py"],
        "factors": [
            "Parcs et jardins publics",
            "Giratoires",
            "Espaces jeux et pietonnier",
            "Friche naturelle",
        ],
        "output_type": "POLYGON",
    },
    {
        "name": "EVA 2015",
        "uncertainty": 3,
        "file": "new_all_eva.shp",
        "actions": eva_actions(
            [[11], [12, 13] + EVA_OPEN_GROUND_CODES, *EVA_LAND_COVER_CODES[1:]],
            simplify=3,
        ),
        "scripts": [
            "strate_arboree.py",
            "strate_basse.py",
            "agricole.py",
            "foret.py",
            "arti.py",
        ],
        "factors": [
            "Strate arborée",
            "Strate basse et pelouse",
            "Espaces agricoles",
            "Forêts",
            "Espaces artificialisés",
        ],
        "output_type": "POLYGON",
    },
    {
        "name": "EVA 2015 1m",
        "uncertainty": None,
        "file": "new_all_eva.shp",
        "actions": eva_actions(EVA_LAND_COVER_CODES),
        "factors": [
            "EVA sols nus, friches et milieux herbeux",
            "EVA espaces agricoles",
            "EVA forêts",
            "EVA espaces artificialisés",
        ],
        "output_type": "POLYGON",
    },
    {
        "name": "Place PMR",
        "uncertainty": 0.5,
        "file": "voirie.gpkg",
        "layer_name": "pub_patrimoinevoirie.emplacementpmr",
        "actions": [{"buffer_size": 3}],
        "factors": ["PMR"],
        "output_type": "POLYGON",
    },
    {
        "name": "Auto-partage",
        "uncertainty": 0.5,
        "file": "voirie.gpkg",
        "layer_name": "pub_patrimoinevoirie.stationautopartage",
        "actions": [{"buffer_size": 3}],
        "factors": ["Auto-partage"],
        "output_type": "POLYGON",
    },
]
URL_FILES = [
    {
        "name": "Entrée parking",
        "uncertainty": 1,
        "url": "https://data.grandlyon.com/geoserver/lyon-parc-auto/ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=lyon-parc-auto:lpa_mobilite.entree_parking&outputFormat=GML3&SRSNAME=EPSG:2154&startIndex=0",
        "layer_name": "lpa_mobilite.entree_parking",
        "actions": [{"buffer_size": 5}],
        "scripts": [],
        "factors": ["Entrée parking"],
        "output_type": "POINT",
    },
    {
        "name": "Réseaux gaz",
        "uncertainty": 1,
        "url": "https://opendata.agenceore.fr/data-fair/api/v1/datasets/infrastructures-reseau-gaz/lines",
        "actions": [{"buffer_size": 2, "union": True}],
        "scripts": ["gaz.py"],
        "factors": ["Rsx gaz"],
        "output_type": "LINESTRING",
    },
    {
        "name": "Réseaux souterrains Enedis",
        "uncertainty": None,
        "url": "https://opendata.agenceore.fr/data-fair/api/v1/datasets/reseau-souterrain-basse-tension-bt/lines",
        "actions": [{"buffer_size": 2, "union": True}],
        "scripts": ["souterrain_enedis.py"],
        "factors": ["Rsx souterrains ERDF"],
        "output_type": "LINESTRING",
    },
    {
        "name": "Réseaux aériens Enedis",
        "uncertainty": None,
        "url": "https://opendata.agenceore.fr/data-fair/api/v1/datasets/reseau-aerien-basse-tension-bt/lines",
        "actions": [{"buffer_size": 1, "union": True}],
        "scripts": ["aerien_enedis.py"],
        "factors": ["Rsx aériens ERDF"],
        "output_type": "LINESTRING",
    },
    {
        "name": "Quartiers prioritaires de la ville",
        "uncertainty": None,
        "url": "https://data.grandlyon.com/geoserver/metropole-de-lyon/ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=metropole-de-lyon:ter_territoire.quartier_prioritaire_2024_2030&outputFormat=GML3&SRSNAME=EPSG:2154&startIndex=0&sortby=gid",
        "scripts": [""],
        "layer_name": "ter_territoire.quartier_prioritaire_2024_2030",
        "factors": ["QPV"],
        "output_type": "LINESTRING",
    },
    {
        "name": "Réseau Fibre",
        "uncertainty": None,
        "url": "https://data.grandlyon.com/geoserver/metropole-de-lyon/ows"
        "?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&"
        "typename=metropole-de-lyon:tel_telecom.fibre_rip_thd&"
        "outputFormat=GML3&SRSNAME=EPSG:2154&startIndex=0&sortBy=gid",
        "scripts": ["fibre.py"],
        "layer_name": "tel_telecom.fibre_rip_thd",
        "actions": [{"buffer_size": 2, "union": True}],
        "factors": ["Réseau Fibre"],
        "output_type": "LINESTRING",
    },
    {
        "name": "Plan eau",
        "uncertainty": 0.5,
        "url": "https://data.grandlyon.com/geoserver/metropole-de-lyon/ows"
        "?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&"
        "typename=metropole-de-lyon:fpc_fond_plan_communaut.fpcplandeau&"
        "outputFormat=GML3&SRSNAME=EPSG:2154&startIndex=0&sortBy=gid",
        "actions": [{"explode": True, "buffer_size": 0.1, "union": True}],
        "scripts": ["plan_eau.py"],
        "layer_name": "fpc_fond_plan_communaut.fpcplandeau",
        "factors": ["Plan eau"],
        "output_type": "POLYGON",
    },
    {
        "name": "Ponts",
        "uncertainty": 0.5,
        "url": "https://data.grandlyon.com/geoserver/metropole-de-lyon/"
        "ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&"
        "typename=metropole-de-lyon:fpc_fond_plan_communaut.fpcpont&"
        "outputFormat=GML3&SRSNAME=EPSG:2154&startIndex=0&sortBy=gid",
        "actions": [{"buffer_size": 2}],
        "scripts": ["pont.py"],
        "layer_name": "fpc_fond_plan_communaut.fpcpont",
        "factors": ["Ponts"],
        "output_type": "POLYGON",
    },
    {
        "name": "Arbres alignements Métropole",
        "uncertainty": 0.5,
        "url": "https://data.grandlyon.com/geoserver/metropole-de-lyon/"
        "ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&"
        "typename=metropole-de-lyon:"
        "abr_arbres_alignement.abrarbre&outputFormat=GML3&"
        "SRSNAME=EPSG:2154&startIndex=0&sortBy=gid",
        "layer_name": "abr_arbres_alignement.abrarbre",
        "scripts": ["arbre_souche.py", "arbre.py"],
        "actions": [
            {
                "filters": [
                    {
                        "name": "genre",
                        "value": "Emplacement libre",
                    },
                    {
                        "name": "genre",
                        "value": "Souche",
                    },
                ],
                "buffer_size": 1,
            },
            {
                "exclude": {"name": "genre", "value": ["Emplacement libre", "Souche"]},
                "buffer": {"distance_column": "circonference_cm"},
                "union": True,
            },
        ],
        "factors": ["Souches ou emplacements libres", "Arbres"],
        "output_type": "POINT",
    },
    {
        "name": "Marchés forains",
        "uncertainty": None,
        "url": "https://download.data.grandlyon.com/wfs/grandlyon",
        "layer_name": "gin_nettoiement.ginmarche",
        "scripts": [],
        "factors": ["Marchés forains"],
        "output_type": "POLYGON",
    },
    {
        "name": "Voies ferrées",
        "uncertainty": 0.5,
        "url": "https://download.data.grandlyon.com/wfs/grandlyon",
        "layer_name": "fpc_fond_plan_communaut.fpcvoieferree",
        "actions": [{"buffer_size": 1, "union": True}],
        "scripts": ["voie_ferree.py"],
        "factors": ["Voies ferrées"],
        "output_type": "LINESTRING",
    },
    {
        "name": "Velov",
        "uncertainty": 1,
        "url": "https://data.grandlyon.com/geoserver/metropole-de-lyon/"
        "ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&"
        "typename=metropole-de-lyon:"
        "pvo_patrimoine_voirie.pvostationvelov&"
        "outputFormat=GML3&SRSNAME=EPSG:2154"
        "&startIndex=0&sortBy=gid",
        "layer_name": "pvo_patrimoine_voirie.pvostationvelov",
        "scripts": ["velov.py"],
        "actions": [
            {"buffer_size": 6, "union": True},
        ],
        "factors": ["Station velov"],
        "output_type": "POINT",
    },
    {
        "name": "Aerodrome",
        "uncertainty": 1,
        "url": "https://data.grandlyon.com/geoserver/metropole-de-lyon/"
        "ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&"
        "typename=metropole-de-lyon:adr_voie_lieu.adraerodrome&"
        "outputFormat=GML3&"
        "SRSNAME=EPSG:2154&startIndex=0&sortBy=gid",
        "layer_name": "adr_voie_lieu.adraerodrome",
        "scripts": [""],
        "actions": [{}],
        "factors": ["Aerodrome"],
        "output_type": "POLYGON",
    },
    {
        "name": "Arrêts transport en",
        "uncertainty": 1,
        "url": "https://data.grandlyon.com/geoserver/sytral/"
        "ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature"
        "&typename=sytral:tcl_sytral.tclarret&outputFormat=GML3"
        "&SRSNAME=EPSG:2154&startIndex=0&sortBy=gid",
        "layer_name": "tcl_sytral.tclarret",
        "scripts": ["transport.py"],
        "actions": [
            {"buffer_size": 2.5, "union": True},
        ],
        "factors": ["Arrêts transport en commun"],
        "output_type": "POINT",
    },
    {
        "name": "Pistes cyclables",
        "uncertainty": 1,
        "url": "https://data.grandlyon.com/geoserver/metropole-de-lyon/"
        "ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&"
        "typename=metropole-de-lyon:"
        "pvo_patrimoine_voirie.pvoamenagementcyclable&"
        "outputFormat=GML3&SRSNAME=EPSG:2154&"
        "startIndex=0&sortBy=gid",
        "layer_name": "pvo_patrimoine_voirie.pvoamenagementcyclable",
        "actions": [{"buffer_size": 2, "union": True}],
        "scripts": ["piste_cyclable.py"],
        "factors": ["Pistes cyclable"],
        "output_type": "LINESTRING",
    },
    {
        "name": "Tracé de métro",
        "uncertainty": 1,
        "url": "https://data.grandlyon.com/geoserver/sytral/"
        "ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&"
        "typename=sytral:tcl_sytral.tcllignemf_2_0_0&"
        "outputFormat=GML3&"
        "SRSNAME=EPSG:2154&startIndex=0&sortBy=gid",
        "layer_name": "tcl_sytral.tcllignemf_2_0_0",
        "actions": [{"buffer_size": 25, "union": True}],
        "scripts": ["metro_funiculaire.py"],
        "factors": ["Tracé de métro"],
        "output_type": "LINESTRING",
    },
    {
        "name": "Tracé de tramway",
        "uncertainty": 1,
        "url": "https://data.grandlyon.com/geoserver/sytral/"
        "ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&"
        "typename=sytral:tcl_sytral.tcllignetram_2_0_0&"
        "outputFormat=GML3&"
        "SRSNAME=EPSG:2154&startIndex=0&sortBy=gid",
        "layer_name": "tcl_sytral.tcllignetram_2_0_0",
        "actions": [{"buffer_size": 3.5, "union": True}],
        "scripts": ["tram.py"],
        "factors": ["Tracé de tramway"],
        "output_type": "LINESTRING",
    },
    {
        "name": "Tracé de bus",
        "uncertainty": 1,
        "url": "https://data.grandlyon.com/geoserver/sytral/"
        "ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&"
        "typename=sytral:tcl_sytral.tcllignebus_2_0_0&"
        "outputFormat=GML3&SRSNAME=EPSG:2154&"
        "startIndex=0&sortBy=gid",
        "layer_name": "tcl_sytral.tcllignebus_2_0_0",
        "actions": [{"buffer_size": 1.5, "union": True}],
        "scripts": ["bus.py"],
        "factors": ["Tracé de bus"],
        "output_type": "LINESTRING",
    },
    {
        "name": "Réseau chaleur urbain",
        "uncertainty": None,
        "url": "https://data.grandlyon.com/geoserver/metropole-de-lyon/"
        "ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&"
        "typename=metropole-de-lyon:nrj_energie.rcu_canalisation&"
        "outputFormat=GML3&SRSNAME=EPSG:2154&startIndex=0&sortBy=gid",
        "layer_name": "nrj_energie.rcu_canalisation",
        "actions": [{"buffer_size": 2, "union": True}],
        "scripts": ["rsx_chaleur.py"],
        "factors": ["Réseau de chaleur urbain"],
        "output_type": "LINESTRING",
    },
    {
        "name": "Friches",
        "uncertainty": None,
        "url": "https://apidf-preprod.cerema.fr/cartofriches/geofriches/",
        "layer_name": "",
        "scripts": None,
        "factors": ["Friches"],
        "output_type": "POLYGON",
    },
    {
        "name": "Bâtiments",
        "uncertainty": 1,
        "url": "https://data.geopf.fr/wfs/ows",
        "layer_name": "",
        "scripts": ["batiment.py", "facade.py"],
        "actions": [
            {},
            {"buffer_size": 2, "union": True},
        ],
        "factors": ["Bâtiments", "Proximité façade"],
        "output_type": "POLYGON",
    },
    {
        "name": "Local Climate Zone",
        "uncertainty": None,
        "url": "https://www.data.gouv.fr/fr/datasets/r/e0c0f5e4-c8bb-4d33-aec9-ba16b5736102",
        "output_type": "POLYGON",
        "factors": "",
    },
]

LCZ = {
    "1": "Ensemble compact de tours",
    "2": "Ensemble compact d'immeubles",
    "3": "Ensemble compact de maisons",
    "4": "Ensemble de tours espacées",
    "5": "Ensemble d'immeubles espacés",
    "6": "Ensemble de maisons espacées",
    "8": "Bâtiments bas de grande emprise",
    "9": "Implantation diffuse de maisons",
    "A": "Espace densément arboré",
    "B": "Espace arboré clairsemé",
    "C": "Espace végétalisé hétérogène",
    "D": "Végétation basse",
    "E": "Sol imperméable naturel ou artificiel",
    "F": "Sol nu perméable",
    "G": "Surface en eau",
}

PUBLIC_BUILDINGS = {
    "bdtopo_url": "https://data.geopf.fr/wfs/ows",
    "bdtopo_typename": "BDTOPO_V3:zone_d_activite_ou_d_interet",
    "bdtopo_columns": [
        "cleabs",
        "categorie",
        "nature",
        "nature_detaillee",
        "toponyme",
        "fictif",
        "etat_de_l_objet",
        "identifiants_sources",
        "insee_commune",
    ],
    "grandlyon_url": "https://data.grandlyon.com/geoserver/metropole-de-lyon/ows",
    "grandlyon_edu_layers": [
        "metropole-de-lyon:edu_education.ecole",
        "metropole-de-lyon:edu_education.college",
        "metropole-de-lyon:edu_education.lycee",
    ],
    "grandlyon_creche_layer": "metropole-de-lyon:car_care.carcreche_latest",
    "creche_public_managers": ["Collectivité Locale"],
    "categories": {
        "Science et enseignement": "enseignement",
        "Santé": "sante",
        "Administratif ou militaire": "administratif",
        "Culture et loisirs": "culture",
        "Petite enfance": "petite_enfance",
    },
    "dropped_nature_details": ["Crèche"],
    "kept_natures": {
        "Santé": {
            "Hôpital": None,
            "Etablissement hospitalier": None,
            "Maison de retraite": None,
            "Résidence autonomie": None,
        },
        "Administratif ou militaire": {"Mairie": None},
        "Culture et loisirs": {
            "Musée": None,
            "Ecomusée": None,
            "Centre de documentation": [
                "Bibliothèque",
                "Médiathèque",
                "Archives départementales",
            ],
        },
    },
    "state_in_service": "En service",
    "nested_footprint_ratio": 0.99,
}
