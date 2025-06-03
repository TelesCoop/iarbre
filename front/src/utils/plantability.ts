import {
  PlantabilityImpact,
  PlantabilityLandUseKeys,
  PlantabilityScore
} from "@/types/plantability"

export function getPlantabilityScore(id: number): string {
  if (id < 2) return PlantabilityScore.IMPOSSIBLE
  if (id < 4) return PlantabilityScore.VERY_CONSTRAINED
  if (id < 6) return PlantabilityScore.CONSTRAINED
  if (id < 8) return PlantabilityScore.NEUTRAL
  if (id < 10) return PlantabilityScore.FAVORED
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
  [PlantabilityLandUseKeys.ASSAINISSEMENT]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.RESEAU_FIBRE]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.RESEAU_CHALEUR_URBAIN]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.RSX_GAZ]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.RSX_SOUTERRAINS_ERDF]: PlantabilityImpact.NEGATIVE,

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

  // Autres (classification à déterminer)
  [PlantabilityLandUseKeys.PLAN_EAU]: PlantabilityImpact.POSITIVE,
  [PlantabilityLandUseKeys.ESPACES_ARTIFICIALISES]: PlantabilityImpact.NEGATIVE,
  [PlantabilityLandUseKeys.RSX_AERIENS_ERDF]: PlantabilityImpact.NEGATIVE
}
