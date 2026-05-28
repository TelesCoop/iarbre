import {
  PlantabilityImpact,
  PlantabilityLandUseKeys,
  PlantabilityMetaCategory,
  PlantabilityScore
} from "@/types/plantability"
import { metaFactorColors } from "@/theme/iArbre"

export enum PlantabilityScoreThreshold {
  IMPOSSIBLE = 0,
  VERY_CONSTRAINED = 2,
  CONSTRAINED = 4,
  NEUTRAL = 6,
  FAVORED = 8,
  VERY_FAVORED = 10
}

export const PLANTABILITY_SCORES = Object.values(PlantabilityScoreThreshold) as number[]
export const PLANTABILITY_SCORES_STR = PLANTABILITY_SCORES.map(String)

export function getPlantabilityScore(id: number): string {
  if (id < PlantabilityScoreThreshold.VERY_CONSTRAINED) return PlantabilityScore.IMPOSSIBLE
  if (id < PlantabilityScoreThreshold.CONSTRAINED) return PlantabilityScore.VERY_CONSTRAINED
  if (id < PlantabilityScoreThreshold.NEUTRAL) return PlantabilityScore.CONSTRAINED
  if (id < PlantabilityScoreThreshold.FAVORED) return PlantabilityScore.NEUTRAL
  if (id < PlantabilityScoreThreshold.VERY_FAVORED) return PlantabilityScore.FAVORED
  return PlantabilityScore.VERY_FAVORED
}

export const PLANTABILITY_COLOR_MAP = [
  0,
  "#C4C4C4",
  1,
  "#C4C4C4",
  2,
  "#BF5A16",
  3,
  "#BF5A16",
  4,
  "#DDAD14",
  5,
  "#DDAD14",
  6,
  "#A6CC4A",
  7,
  "#A6CC4A",
  8,
  "#55B250",
  9,
  "#55B250",
  10,
  "#025400",
  "purple"
]

export const PLANTABILITY_EMOJIS: Record<PlantabilityLandUseKeys, string> = {
  [PlantabilityLandUseKeys.RESEAUX_INFRASTRUCTURES]: "🔧",
  [PlantabilityLandUseKeys.SOUCHES_EMPLACEMENTS_LIBRES]: "🪵",
  [PlantabilityLandUseKeys.ARBRES]: "🌳",
  [PlantabilityLandUseKeys.AERODROME]: "✈️",
  [PlantabilityLandUseKeys.PARKINGS]: "🅿️",
  [PlantabilityLandUseKeys.SIGNALISATION_TRICOLORE]: "🚦",
  [PlantabilityLandUseKeys.STATION_VELOV]: "🚲",
  [PlantabilityLandUseKeys.ARRETS_TRANSPORT]: "🚌",
  [PlantabilityLandUseKeys.PROXIMITE_FACADE]: "🏢",
  [PlantabilityLandUseKeys.BATIMENTS]: "🏗️",
  [PlantabilityLandUseKeys.FRICHES]: "🌾",
  [PlantabilityLandUseKeys.ASSAINISSEMENT]: "🚰",
  [PlantabilityLandUseKeys.PARCS_JARDINS]: "🌻",
  [PlantabilityLandUseKeys.GIRATOIRES]: "🔄",
  [PlantabilityLandUseKeys.ESPACES_JEUX_PIETONNIER]: "🛝",
  [PlantabilityLandUseKeys.FRICHE_NATURELLE]: "🌿",
  [PlantabilityLandUseKeys.RESEAU_FIBRE]: "🌐",
  [PlantabilityLandUseKeys.MARCHES_FORAINS]: "🏪",
  [PlantabilityLandUseKeys.PISTES_CYCLABLE]: "🚴",
  [PlantabilityLandUseKeys.PLAN_EAU]: "💧",
  [PlantabilityLandUseKeys.PONTS]: "🌉",
  [PlantabilityLandUseKeys.RESEAU_CHALEUR_URBAIN]: "🔥",
  [PlantabilityLandUseKeys.VOIES_FERREES]: "🚂",
  [PlantabilityLandUseKeys.STRATE_ARBOREE]: "🌲",
  [PlantabilityLandUseKeys.STRATE_BASSE_PELOUSE]: "🌱",
  [PlantabilityLandUseKeys.ESPACES_AGRICOLES]: "🚜",
  [PlantabilityLandUseKeys.FORETS]: "🌲",
  [PlantabilityLandUseKeys.ESPACES_ARTIFICIALISES]: "🏙️",
  [PlantabilityLandUseKeys.TRACE_METRO]: "🚇",
  [PlantabilityLandUseKeys.TRACE_TRAMWAY]: "🚊",
  [PlantabilityLandUseKeys.TRACE_BUS]: "🚍",
  [PlantabilityLandUseKeys.RSX_GAZ]: "⛽",
  [PlantabilityLandUseKeys.RSX_SOUTERRAINS_ERDF]: "⚡",
  [PlantabilityLandUseKeys.RSX_AERIENS_ERDF]: "🔌",
  [PlantabilityLandUseKeys.PMR]: "♿",
  [PlantabilityLandUseKeys.AUTO_PARTAGE]: "🚗"
}

export const PLANTABILITY_FACTORS_IMPACT: Record<PlantabilityLandUseKeys, PlantabilityImpact> = {
  // Networks and infrastructure (NEGATIVE)
  [PlantabilityLandUseKeys.RESEAUX_INFRASTRUCTURES]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.ASSAINISSEMENT]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.RESEAU_FIBRE]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.RESEAU_CHALEUR_URBAIN]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.RSX_GAZ]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.RSX_SOUTERRAINS_ERDF]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.RSX_AERIENS_ERDF]: PlantabilityImpact.NEGATIVE,

  // Infrastructure de transport (NEGATIF)
  [PlantabilityLandUseKeys.AERODROME]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.PARKINGS]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.SIGNALISATION_TRICOLORE]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.STATION_VELOV]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.ARRETS_TRANSPORT]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.PISTES_CYCLABLE]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.PONTS]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.VOIES_FERREES]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.TRACE_METRO]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.TRACE_TRAMWAY]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.TRACE_BUS]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.PMR]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.AUTO_PARTAGE]: PlantabilityImpact.NEGATIVE,

  // Bâtiments (NEGATIF)
  [PlantabilityLandUseKeys.PROXIMITE_FACADE]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.BATIMENTS]: PlantabilityImpact.NEGATIVE,

  // Espaces verts (POSITIF)
  [PlantabilityLandUseKeys.SOUCHES_EMPLACEMENTS_LIBRES]: PlantabilityImpact.POSITIVE,
  [PlantabilityLandUseKeys.ARBRES]: PlantabilityImpact.POSITIVE,
  [PlantabilityLandUseKeys.PARCS_JARDINS]: PlantabilityImpact.POSITIVE,
  [PlantabilityLandUseKeys.FRICHE_NATURELLE]: PlantabilityImpact.POSITIVE,
  [PlantabilityLandUseKeys.STRATE_ARBOREE]: PlantabilityImpact.POSITIVE,
  [PlantabilityLandUseKeys.STRATE_BASSE_PELOUSE]: PlantabilityImpact.POSITIVE,
  [PlantabilityLandUseKeys.ESPACES_AGRICOLES]: PlantabilityImpact.POSITIVE,
  [PlantabilityLandUseKeys.FORETS]: PlantabilityImpact.POSITIVE,

  // Aménagements urbains (POSITIF)
  [PlantabilityLandUseKeys.GIRATOIRES]: PlantabilityImpact.POSITIVE,
  [PlantabilityLandUseKeys.ESPACES_JEUX_PIETONNIER]: PlantabilityImpact.POSITIVE,
  [PlantabilityLandUseKeys.FRICHES]: PlantabilityImpact.POSITIVE,
  [PlantabilityLandUseKeys.MARCHES_FORAINS]: PlantabilityImpact.POSITIVE,

  // Plans d'eau (NEGATIF)
  [PlantabilityLandUseKeys.PLAN_EAU]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.ESPACES_ARTIFICIALISES]: PlantabilityImpact.NEGATIVE
}

export const PLANTABILITY_FACTORS_META_CATEGORIES = {
  [PlantabilityLandUseKeys.RESEAUX_INFRASTRUCTURES]:
    PlantabilityMetaCategory.RESEAUX_INFRASTRUCTURES,
  [PlantabilityLandUseKeys.ASSAINISSEMENT]: PlantabilityMetaCategory.RESEAUX_INFRASTRUCTURES,
  [PlantabilityLandUseKeys.RESEAU_FIBRE]: PlantabilityMetaCategory.RESEAUX_INFRASTRUCTURES,
  [PlantabilityLandUseKeys.RESEAU_CHALEUR_URBAIN]: PlantabilityMetaCategory.RESEAUX_INFRASTRUCTURES,
  [PlantabilityLandUseKeys.RSX_GAZ]: PlantabilityMetaCategory.RESEAUX_INFRASTRUCTURES,
  [PlantabilityLandUseKeys.RSX_SOUTERRAINS_ERDF]: PlantabilityMetaCategory.RESEAUX_INFRASTRUCTURES,
  [PlantabilityLandUseKeys.RSX_AERIENS_ERDF]: PlantabilityMetaCategory.RESEAUX_INFRASTRUCTURES,

  [PlantabilityLandUseKeys.AERODROME]: PlantabilityMetaCategory.INFRASTRUCTURE_TRANSPORT,
  [PlantabilityLandUseKeys.PARKINGS]: PlantabilityMetaCategory.INFRASTRUCTURE_TRANSPORT,
  [PlantabilityLandUseKeys.SIGNALISATION_TRICOLORE]:
    PlantabilityMetaCategory.INFRASTRUCTURE_TRANSPORT,
  [PlantabilityLandUseKeys.STATION_VELOV]: PlantabilityMetaCategory.INFRASTRUCTURE_TRANSPORT,
  [PlantabilityLandUseKeys.ARRETS_TRANSPORT]: PlantabilityMetaCategory.INFRASTRUCTURE_TRANSPORT,
  [PlantabilityLandUseKeys.PISTES_CYCLABLE]: PlantabilityMetaCategory.INFRASTRUCTURE_TRANSPORT,
  [PlantabilityLandUseKeys.PONTS]: PlantabilityMetaCategory.INFRASTRUCTURE_TRANSPORT,
  [PlantabilityLandUseKeys.VOIES_FERREES]: PlantabilityMetaCategory.INFRASTRUCTURE_TRANSPORT,
  [PlantabilityLandUseKeys.TRACE_METRO]: PlantabilityMetaCategory.INFRASTRUCTURE_TRANSPORT,
  [PlantabilityLandUseKeys.TRACE_TRAMWAY]: PlantabilityMetaCategory.INFRASTRUCTURE_TRANSPORT,
  [PlantabilityLandUseKeys.TRACE_BUS]: PlantabilityMetaCategory.INFRASTRUCTURE_TRANSPORT,
  [PlantabilityLandUseKeys.PMR]: PlantabilityMetaCategory.INFRASTRUCTURE_TRANSPORT,
  [PlantabilityLandUseKeys.AUTO_PARTAGE]: PlantabilityMetaCategory.INFRASTRUCTURE_TRANSPORT,

  [PlantabilityLandUseKeys.PROXIMITE_FACADE]: PlantabilityMetaCategory.BATIMENTS,
  [PlantabilityLandUseKeys.BATIMENTS]: PlantabilityMetaCategory.BATIMENTS,

  [PlantabilityLandUseKeys.SOUCHES_EMPLACEMENTS_LIBRES]: PlantabilityMetaCategory.ESPACES_VERTS,
  [PlantabilityLandUseKeys.ARBRES]: PlantabilityMetaCategory.ESPACES_VERTS,
  [PlantabilityLandUseKeys.PARCS_JARDINS]: PlantabilityMetaCategory.ESPACES_VERTS,
  [PlantabilityLandUseKeys.FRICHE_NATURELLE]: PlantabilityMetaCategory.ESPACES_VERTS,
  [PlantabilityLandUseKeys.STRATE_ARBOREE]: PlantabilityMetaCategory.ESPACES_VERTS,
  [PlantabilityLandUseKeys.STRATE_BASSE_PELOUSE]: PlantabilityMetaCategory.ESPACES_VERTS,
  [PlantabilityLandUseKeys.ESPACES_AGRICOLES]: PlantabilityMetaCategory.ESPACES_VERTS,
  [PlantabilityLandUseKeys.FORETS]: PlantabilityMetaCategory.ESPACES_VERTS,

  [PlantabilityLandUseKeys.GIRATOIRES]: PlantabilityMetaCategory.AMENAGEMENTS_URBAINS,
  [PlantabilityLandUseKeys.ESPACES_JEUX_PIETONNIER]: PlantabilityMetaCategory.AMENAGEMENTS_URBAINS,
  [PlantabilityLandUseKeys.FRICHES]: PlantabilityMetaCategory.AMENAGEMENTS_URBAINS,
  [PlantabilityLandUseKeys.MARCHES_FORAINS]: PlantabilityMetaCategory.AMENAGEMENTS_URBAINS,

  [PlantabilityLandUseKeys.PLAN_EAU]: PlantabilityMetaCategory.PLANS_EAU,
  [PlantabilityLandUseKeys.ESPACES_ARTIFICIALISES]: PlantabilityMetaCategory.PLANS_EAU
}

export const META_FACTOR_COLORS = metaFactorColors

export const ZoomToGridSize: Record<number, number> = {
  10: 100,
  11: 75,
  12: 75,
  13: 30,
  14: 15,
  15: 10,
  16: 5,
  17: 5,
  18: 5
}
