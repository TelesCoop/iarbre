from collections import Counter
from dataclasses import dataclass, field


@dataclass
class TreeSpecies:
    scientific_name: str
    common_name: str
    is_native: bool
    drought_tolerance: str  # "low" | "medium" | "high"
    heat_tolerance: str  # "low" | "medium" | "high"
    max_height_m: int
    canopy_spread: str  # "small" | "medium" | "large"
    is_pioneer: bool = False
    pollution_tolerance: str = "low"  # "low" | "medium" | "high"
    soil_moisture_preference: str = "medium"  # "dry" | "medium" | "wet"
    ecosystem_services: list[str] = field(default_factory=list)
    companion_genera: list[str] = field(default_factory=list)
    lcz_suitability: list[str] = field(default_factory=list)
    description: str = ""


TREE_SPECIES_DB: list[TreeSpecies] = [
    TreeSpecies(
        scientific_name="Quercus robur",
        common_name="Chêne pédonculé",
        is_native=True,
        drought_tolerance="medium",
        heat_tolerance="medium",
        max_height_m=30,
        canopy_spread="large",
        is_pioneer=False,
        pollution_tolerance="medium",
        soil_moisture_preference="medium",
        ecosystem_services=["co2", "biodiversity", "cooling"],
        companion_genera=["Carpinus", "Corylus", "Fagus", "Tilia", "Fraxinus"],
        lcz_suitability=["5", "6", "8", "9", "A", "B", "D"],
        description=(
            "Arbre majestueux à longue durée de vie, excellent support de biodiversité"
            " avec plus de 500 espèces associées."
        ),
    ),
    TreeSpecies(
        scientific_name="Quercus pubescens",
        common_name="Chêne pubescent",
        is_native=True,
        drought_tolerance="high",
        heat_tolerance="high",
        max_height_m=20,
        canopy_spread="medium",
        is_pioneer=False,
        pollution_tolerance="medium",
        soil_moisture_preference="dry",
        ecosystem_services=["co2", "biodiversity", "cooling"],
        companion_genera=["Acer", "Sorbus", "Cornus", "Prunus"],
        lcz_suitability=["4", "5", "6", "8", "9", "A", "B"],
        description=(
            "Très résistant à la sécheresse, parfaitement adapté au réchauffement"
            " climatique en milieu lyonnais."
        ),
    ),
    TreeSpecies(
        scientific_name="Tilia cordata",
        common_name="Tilleul à petites feuilles",
        is_native=True,
        drought_tolerance="medium",
        heat_tolerance="medium",
        max_height_m=25,
        canopy_spread="large",
        is_pioneer=False,
        pollution_tolerance="high",
        soil_moisture_preference="medium",
        ecosystem_services=["co2", "cooling", "biodiversity"],
        companion_genera=["Carpinus", "Acer", "Fagus", "Quercus"],
        lcz_suitability=["4", "5", "6", "8", "9", "A", "B"],
        description="Excellent arbre urbain mellifère, offre une ombre dense et supporte bien la taille.",
    ),
    TreeSpecies(
        scientific_name="Tilia platyphyllos",
        common_name="Tilleul à grandes feuilles",
        is_native=True,
        drought_tolerance="low",
        heat_tolerance="medium",
        max_height_m=30,
        canopy_spread="large",
        is_pioneer=False,
        pollution_tolerance="medium",
        soil_moisture_preference="wet",
        ecosystem_services=["co2", "cooling", "biodiversity"],
        companion_genera=["Carpinus", "Acer", "Fagus", "Fraxinus"],
        lcz_suitability=["5", "6", "9", "A", "B"],
        description="Grand arbre d'ombrage, floraison parfumée attractive pour les pollinisateurs.",
    ),
    TreeSpecies(
        scientific_name="Acer campestre",
        common_name="Érable champêtre",
        is_native=True,
        drought_tolerance="high",
        heat_tolerance="high",
        max_height_m=15,
        canopy_spread="medium",
        is_pioneer=False,
        pollution_tolerance="high",
        soil_moisture_preference="dry",
        ecosystem_services=["biodiversity", "cooling"],
        companion_genera=["Quercus", "Carpinus", "Prunus", "Cornus", "Crataegus"],
        lcz_suitability=["2", "3", "4", "5", "6", "8", "9"],
        description="Très polyvalent en milieu urbain dense, supporte la pollution et la sécheresse.",
    ),
    TreeSpecies(
        scientific_name="Acer platanoides",
        common_name="Érable plane",
        is_native=True,
        drought_tolerance="medium",
        heat_tolerance="medium",
        max_height_m=25,
        canopy_spread="large",
        is_pioneer=False,
        pollution_tolerance="high",
        soil_moisture_preference="medium",
        ecosystem_services=["co2", "cooling"],
        companion_genera=["Tilia", "Fagus", "Fraxinus", "Quercus"],
        lcz_suitability=["4", "5", "6", "8", "9", "A"],
        description="Croissance rapide, ombrage efficace, bonne tolérance aux conditions urbaines.",
    ),
    TreeSpecies(
        scientific_name="Carpinus betulus",
        common_name="Charme commun",
        is_native=True,
        drought_tolerance="medium",
        heat_tolerance="medium",
        max_height_m=20,
        canopy_spread="medium",
        is_pioneer=False,
        pollution_tolerance="medium",
        soil_moisture_preference="medium",
        ecosystem_services=["biodiversity", "cooling"],
        companion_genera=["Quercus", "Fagus", "Tilia", "Corylus"],
        lcz_suitability=["4", "5", "6", "8", "9", "A", "B"],
        description="Très adaptable, supporte bien la taille, feuillage dense marcescent en hiver.",
    ),
    TreeSpecies(
        scientific_name="Fraxinus excelsior",
        common_name="Frêne commun",
        is_native=True,
        drought_tolerance="low",
        heat_tolerance="medium",
        max_height_m=30,
        canopy_spread="large",
        is_pioneer=False,
        pollution_tolerance="medium",
        soil_moisture_preference="wet",
        ecosystem_services=["co2", "biodiversity"],
        companion_genera=["Acer", "Quercus", "Tilia", "Alnus"],
        lcz_suitability=["5", "6", "9", "A", "B", "G"],
        description="Croissance rapide et bois de qualité. Attention : sensible à la chalarose.",
    ),
    TreeSpecies(
        scientific_name="Prunus avium",
        common_name="Merisier",
        is_native=True,
        drought_tolerance="medium",
        heat_tolerance="medium",
        max_height_m=20,
        canopy_spread="medium",
        is_pioneer=False,
        pollution_tolerance="low",
        soil_moisture_preference="medium",
        ecosystem_services=["biodiversity", "cooling"],
        companion_genera=["Quercus", "Carpinus", "Acer", "Sorbus"],
        lcz_suitability=["5", "6", "8", "9", "A", "B"],
        description="Floraison printanière spectaculaire, fruits pour l'avifaune, bel arbre d'ornement.",
    ),
    TreeSpecies(
        scientific_name="Sorbus aucuparia",
        common_name="Sorbier des oiseleurs",
        is_native=True,
        drought_tolerance="medium",
        heat_tolerance="medium",
        max_height_m=12,
        canopy_spread="small",
        is_pioneer=False,
        pollution_tolerance="medium",
        soil_moisture_preference="medium",
        ecosystem_services=["biodiversity"],
        companion_genera=["Betula", "Quercus", "Prunus"],
        lcz_suitability=["3", "4", "5", "6", "8", "9", "A"],
        description="Petit arbre idéal pour espaces restreints, baies très appréciées des oiseaux.",
    ),
    TreeSpecies(
        scientific_name="Alnus glutinosa",
        common_name="Aulne glutineux",
        is_native=True,
        drought_tolerance="low",
        heat_tolerance="low",
        max_height_m=25,
        canopy_spread="medium",
        is_pioneer=True,
        pollution_tolerance="medium",
        soil_moisture_preference="wet",
        ecosystem_services=["co2", "biodiversity"],
        companion_genera=["Salix", "Fraxinus", "Populus"],
        lcz_suitability=["9", "A", "B", "G"],
        description="Fixateur d'azote, idéal en zones humides et ripisylves, croissance rapide.",
    ),
    TreeSpecies(
        scientific_name="Betula pendula",
        common_name="Bouleau verruqueux",
        is_native=True,
        drought_tolerance="medium",
        heat_tolerance="medium",
        max_height_m=20,
        canopy_spread="medium",
        is_pioneer=True,
        pollution_tolerance="medium",
        soil_moisture_preference="dry",
        ecosystem_services=["biodiversity", "cooling"],
        companion_genera=["Quercus", "Sorbus", "Pinus"],
        lcz_suitability=["4", "5", "6", "8", "9", "A", "B"],
        description="Arbre pionnier à croissance rapide, écorce décorative, léger et lumineux.",
    ),
    TreeSpecies(
        scientific_name="Fagus sylvatica",
        common_name="Hêtre commun",
        is_native=True,
        drought_tolerance="low",
        heat_tolerance="low",
        max_height_m=35,
        canopy_spread="large",
        is_pioneer=False,
        pollution_tolerance="low",
        soil_moisture_preference="wet",
        ecosystem_services=["co2", "biodiversity", "cooling"],
        companion_genera=["Quercus", "Carpinus", "Tilia", "Acer"],
        lcz_suitability=["6", "9", "A", "B"],
        description="Arbre majestueux au feuillage dense. Sensible à la sécheresse, préférer en sites frais.",
    ),
    TreeSpecies(
        scientific_name="Salix alba",
        common_name="Saule blanc",
        is_native=True,
        drought_tolerance="low",
        heat_tolerance="medium",
        max_height_m=25,
        canopy_spread="large",
        is_pioneer=True,
        pollution_tolerance="medium",
        soil_moisture_preference="wet",
        ecosystem_services=["biodiversity", "cooling"],
        companion_genera=["Alnus", "Fraxinus", "Populus"],
        lcz_suitability=["9", "A", "B", "G"],
        description="Arbre des milieux humides, croissance très rapide, silhouette élégante.",
    ),
    TreeSpecies(
        scientific_name="Celtis australis",
        common_name="Micocoulier de Provence",
        is_native=False,
        drought_tolerance="high",
        heat_tolerance="high",
        max_height_m=20,
        canopy_spread="large",
        is_pioneer=False,
        pollution_tolerance="high",
        soil_moisture_preference="dry",
        ecosystem_services=["cooling", "biodiversity"],
        companion_genera=["Quercus", "Acer", "Prunus"],
        lcz_suitability=["2", "3", "4", "5", "6", "8"],
        description=(
            "Excellente tolérance à la chaleur et la sécheresse,"
            " sub-méditerranéen adapté au climat lyonnais futur."
        ),
    ),
    TreeSpecies(
        scientific_name="Melia azedarach",
        common_name="Mélia",
        is_native=False,
        drought_tolerance="high",
        heat_tolerance="high",
        max_height_m=15,
        canopy_spread="medium",
        is_pioneer=False,
        pollution_tolerance="medium",
        soil_moisture_preference="dry",
        ecosystem_services=["cooling"],
        companion_genera=["Celtis", "Prunus"],
        lcz_suitability=["2", "3", "4", "5", "6"],
        description="Arbre ornemental résistant à la chaleur, floraison parfumée, adapté au réchauffement climatique.",
    ),
    TreeSpecies(
        scientific_name="Styphnolobium japonicum",
        common_name="Sophora du Japon",
        is_native=False,
        drought_tolerance="high",
        heat_tolerance="high",
        max_height_m=20,
        canopy_spread="large",
        is_pioneer=False,
        pollution_tolerance="high",
        soil_moisture_preference="dry",
        ecosystem_services=["cooling", "co2"],
        companion_genera=["Tilia", "Acer", "Celtis"],
        lcz_suitability=["2", "3", "4", "5", "6", "8"],
        description=(
            "Arbre urbain éprouvé, floraison estivale tardive,"
            " très bonne tolérance à la chaleur et la pollution."
        ),
    ),
    TreeSpecies(
        scientific_name="Zelkova serrata",
        common_name="Zelkova du Japon",
        is_native=False,
        drought_tolerance="medium",
        heat_tolerance="high",
        max_height_m=25,
        canopy_spread="large",
        is_pioneer=False,
        pollution_tolerance="medium",
        soil_moisture_preference="medium",
        ecosystem_services=["cooling", "co2"],
        companion_genera=["Tilia", "Acer", "Carpinus"],
        lcz_suitability=["3", "4", "5", "6", "8"],
        description="Port élégant en vase, excellent substitut à l'orme, très utilisé en alignement urbain.",
    ),
    TreeSpecies(
        scientific_name="Koelreuteria paniculata",
        common_name="Savonnier",
        is_native=False,
        drought_tolerance="high",
        heat_tolerance="high",
        max_height_m=12,
        canopy_spread="medium",
        is_pioneer=False,
        pollution_tolerance="high",
        soil_moisture_preference="dry",
        ecosystem_services=["cooling", "biodiversity"],
        companion_genera=["Acer", "Prunus", "Celtis"],
        lcz_suitability=["2", "3", "4", "5", "6", "8"],
        description="Petit arbre coloré, floraison jaune estivale puis fruits décoratifs, très résistant en ville.",
    ),
]

TOLERANCE_SCORES = {"low": 0, "medium": 1, "high": 2}

COMPACT_LCZ = {"1", "2", "3"}
RIPARIAN_SPECIES = {"Alnus glutinosa", "Salix alba"}
WATER_LCZ = {"G"}


LCZ_DESCRIPTIONS = {
    "1": "Bâti compact de grande hauteur (LCZ 1)",
    "2": "Bâti compact de moyenne hauteur (LCZ 2)",
    "3": "Bâti compact de faible hauteur (LCZ 3)",
    "4": "Bâti ouvert de grande hauteur (LCZ 4)",
    "5": "Bâti ouvert de moyenne hauteur (LCZ 5)",
    "6": "Bâti ouvert de faible hauteur (LCZ 6)",
    "7": "Bâti léger de faible hauteur (LCZ 7)",
    "8": "Grands bâtiments de faible hauteur (LCZ 8)",
    "9": "Construction éparse (LCZ 9)",
    "10": "Industrie lourde (LCZ 10)",
    "A": "Arbres denses (LCZ A)",
    "B": "Arbres dispersés (LCZ B)",
    "C": "Buissons (LCZ C)",
    "D": "Herbacé (LCZ D)",
    "E": "Roche/sol nu (LCZ E)",
    "F": "Sol nu / sable (LCZ F)",
    "G": "Eau (LCZ G)",
}


@dataclass
class LczContext:
    """Extracted LCZ detail values for scoring."""

    bur: float = 0
    hre: float = 0
    ror: float = 0
    war: float = 0
    bsr: float = 0

    @classmethod
    def from_details(cls, lcz_details: dict | None) -> "LczContext":
        if not lcz_details:
            return cls()
        return cls(
            bur=lcz_details.get("bur", 0),
            hre=lcz_details.get("hre", 0),
            ror=lcz_details.get("ror", 0),
            war=lcz_details.get("war", 0),
            bsr=lcz_details.get("bsr", 0),
        )


def _build_lcz_context(lcz_index: str | None, lcz_details: dict | None) -> str:
    if not lcz_index:
        return ""

    context = LCZ_DESCRIPTIONS.get(lcz_index, f"LCZ {lcz_index}")
    if lcz_details:
        ver = lcz_details.get("ver")
        vhr = lcz_details.get("vhr")
        if ver is not None:
            context += f" — végétation {int(ver * 100)}%"
        if vhr is not None:
            context += f", arborée {int(vhr * 100)}%"

    return context


def _filter_candidates(lcz_index: str | None, lcz: LczContext) -> list[TreeSpecies]:
    candidates = list(TREE_SPECIES_DB)

    if lcz_index:
        if lcz_index in COMPACT_LCZ:
            candidates = [s for s in candidates if s.max_height_m <= 20]
        if lcz_index not in WATER_LCZ and lcz.war <= 0.1:
            candidates = [
                s for s in candidates if s.scientific_name not in RIPARIAN_SPECIES
            ]
        candidates = [s for s in candidates if lcz_index in s.lcz_suitability]

    if lcz.bur > 0.5:
        candidates = [s for s in candidates if s.canopy_spread != "large"]
    if lcz.hre > 0.6:
        candidates = [s for s in candidates if s.max_height_m <= 15]

    return candidates


def _analyze_flora(
    flora: list[dict],
) -> tuple[set[str], list[str], list[str], set[str]]:
    genera_counter: Counter[str] = Counter()
    families_counter: Counter[str] = Counter()

    for plant in flora:
        genus = plant.get("genus", "")
        family = plant.get("family", "")
        if genus:
            genera_counter[genus] += 1
        if family:
            families_counter[family] += 1

    local_genera = set(genera_counter.keys())
    dominant_families = [f for f, _ in families_counter.most_common(5)]
    dominant_genera = [g for g, _ in genera_counter.most_common(5)]
    top_3_genera = set(dominant_genera[:3])

    return local_genera, dominant_families, dominant_genera, top_3_genera


def _score_base_factors(
    species: TreeSpecies,
    local_genera: set[str],
    lcz_index: str | None,
) -> tuple[int, list[str], list[str]]:
    score = 0
    matched_companions = []
    reasoning = []

    for genus in species.companion_genera:
        if genus in local_genera:
            matched_companions.append(genus)
            score += 1

    if matched_companions:
        reasoning.append(
            f"{len(matched_companions)} genre(s) compagnon(s) détecté(s) à proximité "
            f"({', '.join(matched_companions)})"
        )

    if species.is_native:
        score += 2
        reasoning.append("Espèce indigène de la région lyonnaise")

    drought_score = TOLERANCE_SCORES.get(species.drought_tolerance, 0)
    if drought_score >= 1:
        score += 1
    if drought_score == 2:
        reasoning.append("Haute tolérance à la sécheresse, adapté aux canicules")
    elif drought_score == 1:
        reasoning.append("Tolérance modérée à la sécheresse")

    if lcz_index:
        reasoning.append(f"Compatible avec la zone climatique locale (LCZ {lcz_index})")

    return score, matched_companions, reasoning


def _score_plantability(
    species: TreeSpecies, plantability_score: float | None
) -> tuple[int, list[str]]:
    if plantability_score is None:
        return 0, []

    if plantability_score < 4:
        if species.is_pioneer:
            return 2, [
                "Espèce pionnière adaptée aux sols difficiles (plantabilité faible)"
            ]
        return -1, ["Sol difficile peu favorable à cette espèce non pionnière"]

    if plantability_score >= 7:
        return 1, ["Conditions de sol favorables (plantabilité élevée)"]

    return 0, []


def _score_urban_context(
    species: TreeSpecies, lcz: LczContext
) -> tuple[int, list[str]]:
    score = 0
    reasoning = []

    if lcz.bur > 0.5:
        if species.canopy_spread == "small":
            score += 2
            reasoning.append("Petit houppier adapté au bâti dense")
        elif species.canopy_spread == "medium":
            score += 1
            reasoning.append("Houppier moyen compatible avec le bâti dense")

    if lcz.ror > 0.5:
        pollution_scores = {
            "high": (2, "Haute tolérance à la pollution, adapté aux axes routiers"),
            "medium": (1, "Tolérance modérée à la pollution"),
            "low": (
                -1,
                "Sensible à la pollution, zone à forte imperméabilisation routière",
            ),
        }
        entry = pollution_scores.get(species.pollution_tolerance)
        if entry:
            score += entry[0]
            reasoning.append(entry[1])

    return score, reasoning


def _score_diversity(
    species: TreeSpecies, top_3_genera: set[str]
) -> tuple[int, list[str]]:
    species_genus = species.scientific_name.split()[0]
    if species_genus in top_3_genera:
        return -2, [
            f"Genre {species_genus} déjà dominant localement, diversification souhaitée"
        ]
    return 0, []


def _score_inpn(
    species: TreeSpecies, inpn_results: dict[str, bool] | None
) -> tuple[int, list[str]]:
    if inpn_results and inpn_results.get(species.scientific_name, False):
        return 1, ["Présence confirmée en France (INPN/TaxRef)"]
    return 0, []


def _score_soil_moisture(
    species: TreeSpecies, lcz: LczContext
) -> tuple[int, list[str]]:
    if lcz.war > 0.1:
        if species.soil_moisture_preference == "wet":
            return 2, ["Préférence pour les sols humides, zone à proximité d'eau"]
        if species.soil_moisture_preference == "dry":
            return -1, ["Préfère les sols secs, zone humide défavorable"]
    elif lcz.bsr > 0.2:
        if species.soil_moisture_preference == "dry":
            return 2, ["Adapté aux sols secs et drainants"]
        if species.soil_moisture_preference == "wet":
            return -2, ["Besoin en humidité non satisfait, sol sec et drainant"]
    return 0, []


def get_tree_recommendations(
    flora: list[dict],
    lcz_index: str | None,
    lcz_details: dict | None,
    plantability_score: float | None = None,
    inpn_results: dict[str, bool] | None = None,
) -> dict:
    """Generate tree species recommendations based on local flora and LCZ context."""
    local_genera, dominant_families, dominant_genera, top_3_genera = _analyze_flora(
        flora
    )
    lcz = LczContext.from_details(lcz_details)
    candidates = _filter_candidates(lcz_index, lcz)

    scoring_factors = [
        lambda sp: _score_plantability(sp, plantability_score),
        lambda sp: _score_urban_context(sp, lcz),
        lambda sp: _score_diversity(sp, top_3_genera),
        lambda sp: _score_inpn(sp, inpn_results),
        lambda sp: _score_soil_moisture(sp, lcz),
    ]

    scored_recommendations = []
    for species in candidates:
        score, matched_companions, reasoning = _score_base_factors(
            species, local_genera, lcz_index
        )

        for factor in scoring_factors:
            factor_score, factor_reasoning = factor(species)
            score += factor_score
            reasoning.extend(factor_reasoning)

        scored_recommendations.append(
            {
                "scientific_name": species.scientific_name,
                "common_name": species.common_name,
                "score": score,
                "is_native": species.is_native,
                "description": species.description,
                "matched_companions": matched_companions,
                "ecosystem_highlights": species.ecosystem_services[:3],
                "reasoning": reasoning,
                "inpn_validated": bool(
                    inpn_results and inpn_results.get(species.scientific_name, False)
                ),
            }
        )

    scored_recommendations.sort(key=lambda r: r["score"], reverse=True)

    return {
        "local_flora_summary": {
            "total_species_observed": len(
                {p.get("species", "") for p in flora if p.get("species")}
            ),
            "dominant_families": dominant_families,
            "dominant_genera": dominant_genera,
        },
        "lcz_context": _build_lcz_context(lcz_index, lcz_details),
        "recommendations": scored_recommendations[:8],
    }
