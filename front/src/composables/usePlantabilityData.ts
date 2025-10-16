import { computed, type ComputedRef, type Ref } from "vue"
import {
  PlantabilityImpact,
  type PlantabilityLandUse,
  PlantabilityLandUseKeys,
  PlantabilityOccupationLevel,
  PlantabilityMetaCategory,
  type PlantabilityData
} from "@/types/plantability"
import {
  PLANTABILITY_EMOJIS,
  PLANTABILITY_FACTORS_IMPACT,
  PLANTABILITY_FACTORS_META_CATEGORIES
} from "@/utils/plantability"

export interface PlantabilityFactor {
  key: string
  label: string
  value: string
  icon: string
  impact: PlantabilityImpact | null
  occupationLevel: PlantabilityOccupationLevel
}

export interface PlantabilityFactorGroup {
  category: PlantabilityMetaCategory
  label: string
  icon: string
  factors: PlantabilityFactor[]
  hasPositiveImpact: boolean
  hasNegativeImpact: boolean
}

const OCCUPATION_THRESHOLDS = {
  LOW: 0,
  MEDIUM: 33
} as const

// Mapping des catégories avec leurs labels et icônes
const META_CATEGORY_CONFIG = {
  [PlantabilityMetaCategory.RESEAUX_INFRASTRUCTURES]: {
    label: "Réseaux & infrastructures",
    icon: "🔌"
  },
  [PlantabilityMetaCategory.INFRASTRUCTURE_TRANSPORT]: {
    label: "Transport & mobilité",
    icon: "🚇"
  },
  [PlantabilityMetaCategory.BATIMENTS]: {
    label: "Bâtiments",
    icon: "🏢"
  },
  [PlantabilityMetaCategory.ESPACES_VERTS]: {
    label: "Espaces verts",
    icon: "🌳"
  },
  [PlantabilityMetaCategory.AMENAGEMENTS_URBAINS]: {
    label: "Aménagements urbains",
    icon: "🏛️"
  },
  [PlantabilityMetaCategory.PLANS_EAU]: {
    label: "Plans d'eau",
    icon: "💧"
  }
}

export function usePlantabilityData(data: Ref<PlantabilityData>) {
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
    if (typeof data.value?.details === "string") {
      return [] // No land use factors for histogram data
    }

    const landUseData = data.value?.details?.top5LandUse
    if (!landUseData) return []

    return Object.entries(landUseData).map(([key, value]) => {
      const plantabilityLandKey = key as PlantabilityLandUseKeys
      return {
        key,
        label: key,
        value: createFactorLabel(plantabilityLandKey, value!),
        icon: PLANTABILITY_EMOJIS[plantabilityLandKey] || "❓",
        impact: PLANTABILITY_FACTORS_IMPACT[plantabilityLandKey] || null,
        occupationLevel: getOccupationLevel(value!)
      }
    })
  })

  const factorGroups: ComputedRef<PlantabilityFactorGroup[]> = computed(() => {
    const factorsByCategory = new Map<PlantabilityMetaCategory, PlantabilityFactor[]>()
    factors.value.forEach((factor) => {
      const category = PLANTABILITY_FACTORS_META_CATEGORIES[factor.key as PlantabilityLandUseKeys]
      if (category) {
        if (!factorsByCategory.has(category)) {
          factorsByCategory.set(category, [])
        }
        factorsByCategory.get(category)!.push(factor)
      }
    })

    return Array.from(factorsByCategory.entries())
      .map(([category, categoryFactors]) => {
        const config = META_CATEGORY_CONFIG[category] || { label: category, icon: "📊" }
        const hasPositiveImpact = categoryFactors.some(
          (f) => f.impact === PlantabilityImpact.POSITIVE
        )
        const hasNegativeImpact = categoryFactors.some(
          (f) => f.impact === PlantabilityImpact.NEGATIVE
        )

        return {
          category,
          label: config.label,
          icon: config.icon,
          factors: categoryFactors,
          hasPositiveImpact,
          hasNegativeImpact
        }
      })
      .sort((a, b) => a.label.localeCompare(b.label))
  })

  const hasFactors: ComputedRef<boolean> = computed(() => factors.value.length > 0)

  return {
    factors,
    factorGroups,
    hasFactors
  }
}
