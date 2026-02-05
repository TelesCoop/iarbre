<script lang="ts" setup>
import { type PlantabilityData, PlantabilityImpact } from "@/types/plantability"
import { usePlantabilityData } from "@/composables/usePlantabilityData"
import { toRef, computed } from "vue"
import ContextDataListContainer from "@/components/contextData/shared/ContextDataListContainer.vue"
import type { ContextDataFactorGroup } from "@/types/contextData"
import EmptyMessage from "@/components/EmptyMessage.vue"
import PlantabilityDistributionChart from "./PlantabilityDistributionChart.vue"

interface PlantabilityFactorsProps {
  data: PlantabilityData
}

const props = defineProps<PlantabilityFactorsProps>()

const { factorGroups, hasFactors } = usePlantabilityData(toRef(props, "data"))

const genericFactorGroups = computed((): ContextDataFactorGroup[] => {
  return factorGroups.value.map((group) => ({
    category: group.category.toString(),
    label: group.label,
    icon: group.icon,
    factors: group.factors.map((factor) => ({
      key: factor.key,
      label: factor.label,
      value: factor.value,
      icon: factor.icon,
      impact:
        factor.impact === PlantabilityImpact.POSITIVE
          ? "positive"
          : factor.impact === PlantabilityImpact.NEGATIVE
            ? "negative"
            : null
    })),
    hasPositiveImpact: group.hasPositiveImpact,
    hasNegativeImpact: group.hasNegativeImpact
  }))
})

const distributionEntries = computed(() => {
  // Check if distribution is directly available (from polygon selection)
  if (props.data?.distribution) {
    return Object.entries(props.data.distribution).map(([score, count]) => ({
      score: Number(score),
      count: count as number
    }))
  }

  // Legacy format: details as string with JSON array of values
  if (!props.data?.details) return []

  let parsed: any
  if (typeof props.data.details === "string") {
    try {
      parsed = JSON.parse(props.data.details)
    } catch {
      return []
    }
  } else {
    parsed = props.data.details
  }

  // Legacy format: JSON array of values
  if (Array.isArray(parsed)) {
    const values: number[] = parsed.filter((value) => typeof value === "number")

    // Count frequency of each unique value
    const frequencyMap = new Map<number, number>()
    values.forEach((value) => {
      frequencyMap.set(value, (frequencyMap.get(value) || 0) + 1)
    })

    return Array.from(frequencyMap.entries()).map(([score, count]) => ({
      score,
      count
    }))
  }

  // For zoom >= 17 it is props.data.top5LandUse.
  return []
})
</script>

<template>
  <div aria-labelledby="factors-section">
    <template v-if="hasFactors">
      <ContextDataListContainer
        :groups="genericFactorGroups"
        aria-label="Liste des paramètres de plantabilité par catégorie"
        color-scheme="plantability"
      />
    </template>

    <template v-else>
      <div v-if="distributionEntries.length > 0">
        <PlantabilityDistributionChart :entries="distributionEntries" />
        <EmptyMessage
          data-cy="empty-message"
          message="Zoomez plus pour obtenir l'occupation des sols."
        />
      </div>
      <EmptyMessage
        v-else
        data-cy="empty-message"
        message="Pas de données d'occupation des sols ici."
      />
    </template>
  </div>
</template>

<style scoped></style>
