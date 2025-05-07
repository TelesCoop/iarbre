export enum PlantabilityScore {
  IMPOSSIBLE = "Plantation impossible",
  VERY_CONSTRAINED = "Plantation très contrainte",
  CONSTRAINED = "Plantation contrainte",
  NEUTRAL = "Plantation neutre",
  FAVORED = "Plantation favorisée",
  VERY_FAVORED = "Plantation très favorisée"
}

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
