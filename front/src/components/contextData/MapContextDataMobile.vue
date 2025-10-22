<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import CircularScore from "@/components/shared/CircularScore.vue"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"

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

  if (!contextData) return null

  switch (mapStore.selectedDataType) {
    case DataType.PLANTABILITY: {
      const data = contextData as PlantabilityData
      if (data.plantabilityNormalizedIndice === undefined) return null
      return {
        score: data.plantabilityNormalizedIndice,
        maxScore: 10,
        percentage: data.plantabilityNormalizedIndice * 10,
        label: "plantabilité",
        colorScheme: "plantability"
      }
    }
    case DataType.VULNERABILITY: {
      const data = contextData as VulnerabilityData
      if (data.vulnerabilityIndexDay === undefined) return null
      return {
        score: data.vulnerabilityIndexDay,
        maxScore: 9,
        percentage: (data.vulnerabilityIndexDay / 9) * 100,
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
    <div v-else-if="showClimateText" class="text-center text-gray-700">
      <span class="text-lg font-semibold">Zone climatique locale</span><br />
      <span class="text-sm">{{ (mapStore.contextData.data as ClimateData).lczDescription }}</span>
    </div>
  </div>
</template>
