import json
from django.conf import settings

DATA_FILES = [
    {
        "name": "Parkings surfacique",
        "file": "parkingsurfacique.geojson",
        "scripts": None,
        "factors": ["Parkings"],
        "output_type": "POLYGON",
    },
    {
        "name": "SLT",
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
        "file": "assainissement.geojson",
        "scripts": ["assainissement.py"],
        "actions": [{"buffer_size": 1, "explode": True, "union": True}],
        "factors": ["Assainissement"],
        "output_type": "MULTILINESTRING",
    },
    {
        "name": "Espaces publics",
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
        "file": "new_all_eva.shp",
        "actions": [
            {
                "filter": {"name": "gl_2015", "value": 11},
                "explode": True,
                "simplify": 3,
            },
            {
                "filters": [
                    {"name": "gl_2015", "value": value}
                    for value in [12, 13, 14, 16, 17, 361, 362]
                ],
                "explode": True,
                "simplify": 3,
            },
            {
                "filters": [
                    {"name": "gl_2015", "value": value}
                    for value in [
                        211,
                        212,
                        213,
                        214,
                        215,
                        221,
                        222,
                        223,
                        224,
                        225,
                        231,
                        241,
                    ]
                ],
                "explode": True,
                "simplify": 3,
            },
            {
                "filters": [
                    {"name": "gl_2015", "value": value}
                    for value in [
                        311,
                        312,
                        322,
                        331,
                        341,
                        342,
                        351,
                        371,
                        372,
                        374,
                        411,
                        412,
                    ]
                ],
                "explode": True,
                "simplify": 3,
            },
            {
                "filter": {"name": "gl_2015", "value": 15},
                "explode": True,
                "simplify": 3,
            },
        ],
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
        "name": "Réseaux gaz",
        "file": "rsx_gaz.geojson",
        "actions": [{"buffer_size": 2, "union": True}],
        "scripts": ["gaz.py"],
        "factors": ["Rsx gaz"],
        "output_type": "LINESTRING",
    },
    {
        "name": "Réseaux souterrains Enedis",
        "file": "rsx_souterrain_enedis.geojson",
        "actions": [{"buffer_size": 2, "union": True}],
        "scripts": ["souterrain_enedis.py"],
        "factors": ["Rsx souterrains ERDF"],
        "output_type": "LINESTRING",
    },
    {
        "name": "Réseaux aériens Enedis",
        "file": "rsx_aerien_enedis.geojson",
        "actions": [{"buffer_size": 1, "union": True}],
        "scripts": ["aerien_enedis.py"],
        "factors": ["Rsx aériens ERDF"],
        "output_type": "LINESTRING",
    },
    {
        "name": "Place PMR",
        "file": "voirie.gpkg",
        "layer_name": "pub_patrimoinevoirie.emplacementpmr",
        "actions": [{"buffer_size": 3}],
        "factors": ["PMR"],
        "output_type": "POLYGON",
    },
    {
        "name": "Auto-partage",
        "file": "voirie.gpkg",
        "layer_name": "pub_patrimoinevoirie.stationautopartage",
        "actions": [{"buffer_size": 3}],
        "factors": ["Auto-partage"],
        "output_type": "POLYGON",
    },
]
URL_FILES = [
    {
        "name": "Quartiers prioritaires de la ville",
        "url": "https://data.grandlyon.com/geoserver/metropole-de-lyon/ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=metropole-de-lyon:ter_territoire.qpv_2024&outputFormat=GML3&SRSNAME=EPSG:2154&startIndex=0&sortby=gid",
        "scripts": [""],
        "layer_name": "ter_territoire.qpv_2024",
        "factors": ["QPV"],
        "output_type": "LINESTRING",
    },
    {
        "name": "Réseau Fibre",
        "url": "https://data.grandlyon.com/geoserver/metropole-de-lyon/ows"
        "?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&"
        "typename=metropole-de-lyon:tel_telecom.telfibreripthd_1&"
        "outputFormat=GML3&SRSNAME=EPSG:2154&startIndex=0&sortBy=gid",
        "scripts": ["fibre.py"],
        "layer_name": "tel_telecom.telfibreripthd_1",
        "actions": [{"buffer_size": 2, "union": True}],
        "factors": ["Réseau Fibre"],
        "output_type": "LINESTRING",
    },
    {
        "name": "Plan eau",
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
        "url": "https://download.data.grandlyon.com/wfs/grandlyon",
        "layer_name": "gin_nettoiement.ginmarche",
        "scripts": [],
        "factors": ["Marchés forains"],
        "output_type": "POLYGON",
    },
    {
        "name": "Voies ferrées",
        "url": "https://download.data.grandlyon.com/wfs/grandlyon",
        "layer_name": "fpc_fond_plan_communaut.fpcvoieferree",
        "actions": [{"buffer_size": 1, "union": True}],
        "scripts": ["voie_ferree.py"],
        "factors": ["Voies ferrées"],
        "output_type": "LINESTRING",
    },
    {
        "name": "Velov",
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
        "url": "https://apidf-preprod.cerema.fr/cartofriches/geofriches/",
        "layer_name": "",
        "scripts": None,
        "factors": ["Friches"],
        "output_type": "POLYGON",
    },
    {
        "name": "Bâtiments",
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
        "url": "https://www.data.gouv.fr/fr/datasets/r/e0c0f5e4-c8bb-4d33-aec9-ba16b5736102",
        "output_type": "POLYGON",
        "factors": "",
    },
]

with open(settings.SHARED_CONFIG_PATH, "r", encoding="utf-8") as f:
    SHARED_CONFIG = json.load(f)

# Plantability factor.
# The higher, the more plantable it is
# For example, it's easier to plant a tree on wasteland
# than at an airport
FACTORS = SHARED_CONFIG["plantabilityFactors"]

META_FACTORS_MAPPING = SHARED_CONFIG["metaFactorsMapping"]


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

LCZ = SHARED_CONFIG["localClimateZones"]
