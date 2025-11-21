<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import CircularScore from "@/components/shared/CircularScore.vue"
import type { ClimateData } from "@/types/climate"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"

const mapStore = useMapStore()

interface ScoreData {
  score: number
  maxScore: number
  percentage: number
  label: string
  colorScheme: "plantability" | "vulnerability"
}

const scoreData = computed((): ScoreData | null => {
  const contextData = mapStore.contextData.data

  if (!contextData || contextData.length === 0) return null

  // Les données sont déjà agrégées (soit une seule tuile, soit pré-agrégées par le backend)
  const data = contextData[0]

  switch (mapStore.selectedDataType) {
    case DataType.PLANTABILITY: {
      const plantabilityData = data as PlantabilityData
      if (!plantabilityData?.plantabilityNormalizedIndice) return null
      return {
        score: plantabilityData.plantabilityNormalizedIndice,
        maxScore: 10,
        percentage: plantabilityData.plantabilityNormalizedIndice * 10,
        label: "plantabilité",
        colorScheme: "plantability"
      }
    }
    case DataType.VULNERABILITY: {
      const vulnerabilityData = data as VulnerabilityData
      if (!vulnerabilityData?.vulnerabilityIndexDay) return null
      return {
        score: vulnerabilityData.vulnerabilityIndexDay,
        maxScore: 9,
        percentage: (vulnerabilityData.vulnerabilityIndexDay / 9) * 100,
        label: "vulnérabilité",
        colorScheme: "vulnerability"
      }
    }
    case DataType.CLIMATE_ZONE: {
      // Climate zone doesn't use CircularScore, so return null
      return null
    }
    default:
      return null
  }
})

const hasData = computed(() => mapStore.contextData.data.length > 0)
const showClimateText = computed(
  () => mapStore.selectedDataType === DataType.CLIMATE_ZONE && hasData.value
)

const primaryClimateData = computed(() => {
  if (!hasData.value || mapStore.selectedDataType !== DataType.CLIMATE_ZONE) return null
  return mapStore.contextData.data[0] as ClimateData
})
</script>

<template>
  <div
    v-if="hasData"
    class="absolute bottom-20 bg-white rounded-lg shadow-lg p-2 z-40"
    data-cy="map-context-data-mobile"
  >
    <circular-score
      v-if="scoreData"
      :score="scoreData.score"
      :max-score="scoreData.maxScore"
      :percentage="scoreData.percentage"
      :label="scoreData.label"
      :color-scheme="scoreData.colorScheme"
    />
    <div v-else-if="showClimateText && primaryClimateData" class="text-center text-gray-700">
      <span class="text-lg font-semibold">Zone climatique locale</span><br />
      <span class="text-sm">{{ primaryClimateData.lczDescription }}</span>
    </div>
  </div>
</template>
