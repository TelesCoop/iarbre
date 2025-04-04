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
