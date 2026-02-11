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
  const data = mapStore.contextData.data
  if (!data) return null

  switch (mapStore.selectedDataType) {
    case DataType.PLANTABILITY: {
      const plantabilityData = data as PlantabilityData
      const score = plantabilityData.plantabilityNormalizedIndice ?? 0
      return {
        score,
        maxScore: 10,
        percentage: score * 10,
        label: "plantabilité",
        colorScheme: "plantability"
      }
    }
    case DataType.VULNERABILITY: {
      const vulnerabilityData = data as VulnerabilityData
      const score = vulnerabilityData.vulnerabilityIndexDay ?? 0
      return {
        score,
        maxScore: 9,
        percentage: (score / 9) * 100,
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

const hasData = computed(() => mapStore.contextData.data !== null)
const showClimateText = computed(
  () => mapStore.selectedDataType === DataType.CLIMATE_ZONE && hasData.value
)

const primaryClimateData = computed(() => {
  if (!hasData.value || mapStore.selectedDataType !== DataType.CLIMATE_ZONE) return null
  return mapStore.contextData.data as ClimateData
})
</script>

<template>
  <div
    v-if="scoreData || (showClimateText && primaryClimateData)"
    class="absolute bottom-24 left-1/2 -translate-x-1/2 bg-white rounded-lg p-2 z-40"
    data-cy="map-context-data-mobile"
  >
    <CircularScore
      v-if="scoreData"
      :color-scheme="scoreData.colorScheme"
      :label="scoreData.label"
      :max-score="scoreData.maxScore"
      :percentage="scoreData.percentage"
      :score="scoreData.score"
    />
    <div v-else-if="showClimateText && primaryClimateData" class="text-center text-gray-700">
      <span class="text-lg font-semibold">Zone climatique locale</span><br />
      <span class="text-sm">{{ primaryClimateData.lczDescription }}</span>
    </div>
  </div>
</template>
