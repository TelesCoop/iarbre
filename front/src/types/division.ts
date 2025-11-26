import type { PlantabilityScoreThreshold } from "@/utils/plantability"

export type PlantabilityCounts = Record<PlantabilityScoreThreshold, number>

export interface City {
  id: number
  code: string
  name: string
  plantabilityCounts: PlantabilityCounts
  averageNormalizedIndice: number
  averageIndice: number
  vegetationVoirieHaute: number
  vegetationVoirieMoyenne: number
  vegetationVoirieBasse: number
  vegetationVoirieTotal: number
}

export interface Iris {
  id: number
  code: string
  name: string
  city: number
  plantabilityCounts: PlantabilityCounts
  averageNormalizedIndice: number
  averageIndice: number
}
