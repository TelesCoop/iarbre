from django.db.models import TextChoices


class LandCoverClass(TextChoices):
    BATIMENT = "batiment", "Bâtiment"
    ZONE_PERMEABLE = "zone_permeable", "Zone perméable"
    ZONE_IMPERMEABLE = "zone_impermeable", "Zone imperméable"
    PISCINE = "piscine", "Piscine"
    SOL_NU = "sol_nu", "Sol nu"
    SURFACE_EAU = "surface_eau", "Surface eau"
    NEIGE = "neige", "Neige"
    CONIFERE = "conifere", "Conifère"
    FEUILLU = "feuillu", "Feuillu"
    BROUSSAILLE = "broussaille", "Broussaille"
    VIGNE = "vigne", "Vigne"
    PELOUSE_URBAINE = "pelouse_urbaine", "Pelouse urbaine"
    CULTURE = "culture", "Culture"
    TERRE_LABOUREE = "terre_labouree", "Terre labourée"
    SERRE = "serre", "Serre"
    PLANTATION_ARBRES = "plantation_arbres", "Plantation d'arbres"
    PATURAGE = "paturage", "Pâturage"
    PRAIRIE_NATURELLE = "prairie_naturelle", "Prairie naturelle"
    FOURRE = "fourre", "Fourré"


CLASS_TO_LAND_COVER = {
    1: LandCoverClass.BATIMENT,
    2: LandCoverClass.ZONE_PERMEABLE,
    3: LandCoverClass.ZONE_IMPERMEABLE,
    4: LandCoverClass.PISCINE,
    5: LandCoverClass.SOL_NU,
    6: LandCoverClass.SURFACE_EAU,
    7: LandCoverClass.NEIGE,
    8: LandCoverClass.CONIFERE,
    9: LandCoverClass.FEUILLU,
    10: LandCoverClass.BROUSSAILLE,
    11: LandCoverClass.VIGNE,
    12: LandCoverClass.PELOUSE_URBAINE,
    13: LandCoverClass.CULTURE,
    14: LandCoverClass.TERRE_LABOUREE,
    15: LandCoverClass.SERRE,
    100: LandCoverClass.PLANTATION_ARBRES,
    120: LandCoverClass.PATURAGE,
    121: LandCoverClass.PRAIRIE_NATURELLE,
    122: LandCoverClass.FOURRE,
}

CLASS_TO_BINARY = {
    1: False,
    2: False,
    3: False,
    4: False,
    5: None,
    6: None,
    7: None,
    8: True,
    9: True,
    10: True,
    11: False,
    12: False,
    13: False,
    14: False,
    15: False,
    100: False,
    120: False,
    121: True,
    122: True,
}
