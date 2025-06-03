import { computed, type ComputedRef } from "vue"
import {
  PlantabilityImpact,
  PlantabilityLandUseKeys,
  PlantabilityOccupationLevel,
  type PlantabilityTile
} from "@/types/plantability"
import { PLANTABILITY_EMOJIS, PLANTABILITY_FACTORS_IMPACT } from "@/utils/plantability"

interface PlantabilityFactor {
  key: string
  label: string
  value: string
  icon: string
  impact: PlantabilityImpact | null
  occupationLevel: PlantabilityOccupationLevel
}

const OCCUPATION_THRESHOLDS = {
  LOW: 0,
  MEDIUM: 33
} as const

export function usePlantabilityFactors(dataRef: () => PlantabilityTile) {
  const getOccupationLevel = (value: number): PlantabilityOccupationLevel => {
    if (value < OCCUPATION_THRESHOLDS.LOW) return PlantabilityOccupationLevel.FAIBLE
    if (value < OCCUPATION_THRESHOLDS.MEDIUM) return PlantabilityOccupationLevel.MOYEN
    return PlantabilityOccupationLevel.FORT
  }

  const createFactorLabel = (factorName: PlantabilityLandUseKeys, value: number): string => {
    const factorImpact = PLANTABILITY_FACTORS_IMPACT[factorName]

    if (!factorImpact) return "Impact inconnu"

    const occupationLevel = getOccupationLevel(value)
    return `Impact ${factorImpact} ${occupationLevel}`
  }

  const factors: ComputedRef<PlantabilityFactor[]> = computed(() => {
    const data = dataRef()
    const landUseData = data?.details?.top5LandUse

    if (!landUseData) return []

    return Object.entries(landUseData).map(([key, value]) => {
      const typedKey = key as PlantabilityLandUseKeys

      return {
        key,
        label: key,
        value: createFactorLabel(typedKey, value),
        icon: PLANTABILITY_EMOJIS[typedKey] || "❓",
        impact: PLANTABILITY_FACTORS_IMPACT[typedKey] || null,
        occupationLevel: getOccupationLevel(value)
      }
    })
  })

  const hasFactors: ComputedRef<boolean> = computed(() => factors.value.length > 0)

  return {
    factors,
    hasFactors
  }
}
