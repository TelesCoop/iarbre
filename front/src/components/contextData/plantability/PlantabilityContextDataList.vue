<script lang="ts" setup>
import { type PlantabilityData, PlantabilityImpact } from "@/types/plantability"
import { usePlantabilityData } from "@/composables/usePlantabilityData"
import { toRef, computed } from "vue"
import ContextDataListContainer from "@/components/contextData/shared/ContextDataListContainer.vue"
import type { ContextDataFactorGroup } from "@/types/contextData"
import EmptyMessage from "@/components/EmptyMessage.vue"
import { PLANTABILITY_COLOR_MAP } from "@/utils/plantability"

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

const chartData = computed(() => {
  if (!props.data?.details) return null

  let values: number[]
  if (typeof props.data.details === "string") {
    const parsed = JSON.parse(props.data.details)
    values = Array.isArray(parsed) ? parsed.filter((value) => typeof value === "number") : []
  } else {
    // For zoom >= 17 it is props.data.top5LandUse.
    // Can never happend here but because of type checking need the else
    return null
  }

  // Count frequency of each unique value
  const frequencyMap = new Map<number, number>()
  values.forEach((value) => {
    frequencyMap.set(value, (frequencyMap.get(value) || 0) + 1)
  })

  const scores = Array.from(frequencyMap.keys())
  const labels = scores.map((key) => `Score ${key}`)
  const data = Array.from(frequencyMap.values())

  // Map each score to its corresponding color from PLANTABILITY_COLOR_MAP
  const backgroundColor = scores.map((score) => {
    const colorIndex = PLANTABILITY_COLOR_MAP.indexOf(score)
    return colorIndex !== -1 && colorIndex + 1 < PLANTABILITY_COLOR_MAP.length
      ? PLANTABILITY_COLOR_MAP[colorIndex + 1]
      : "#C4C4C4"
  })

  return {
    labels,
    datasets: [
      {
        data,
        backgroundColor,
        borderWidth: 2,
        borderColor: "#fff"
      }
    ]
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: "bottom",
      onClick: null // don't allow filtering onClick
    },
    title: {
      display: true,
      text: "Distribution des scores de plantabilité sur la zone."
    },
    font: {
      size: 34,
      family: "IBM Plex Mono"
    }
  }
}))
</script>

<template>
  <div aria-labelledby="factors-section">
    <template v-if="hasFactors">
      <context-data-list-container
        :groups="genericFactorGroups"
        color-scheme="plantability"
        aria-label="Liste des paramètres de plantabilité par catégorie"
      />
    </template>

    <template v-else>
      <div v-if="chartData" class="p-4">
        <Chart type="pie" :data="chartData" :options="chartOptions" class="w-full h-64" />
        <empty-message
          data-cy="empty-message"
          message="Zoomez plus pour obtenir l'occupation des sols."
        />
      </div>
      <empty-message
        v-else
        data-cy="empty-message"
        message="Pas de données d'occupation des sols ici."
      />
    </template>
  </div>
</template>

<style scoped></style>
