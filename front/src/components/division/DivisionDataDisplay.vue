<script lang="ts" setup>
import { computed } from "vue"
import type { City, Iris } from "@/types/division"
import CircularScore from "@/components/shared/CircularScore.vue"
import PlantabilityDistributionChart from "@/components/contextData/plantability/PlantabilityDistributionChart.vue"

interface DivisionDataDisplayProps {
  data: City | Iris
}

const props = defineProps<DivisionDataDisplayProps>()

const hasScore = computed(() => props.data.averageNormalizedIndice !== null)

const score = computed(() =>
  hasScore.value ? Number(props.data.averageNormalizedIndice.toFixed(1)) : 0
)

const percentage = computed(() =>
  hasScore.value ? (props.data.averageNormalizedIndice / 10) * 100 : 0
)

const plantabilityEntries = computed(() => {
  if (!props.data.plantabilityCounts) return []
  return Object.entries(props.data.plantabilityCounts)
    .map(([key, value]) => ({
      score: Number(key),
      count: value
    }))
    .sort((a, b) => a.score - b.score)
})

const codeLabel = computed(() => "Code INSEE")
</script>

<template>
  <div>
    <div class="mb-4">
      <p class="text-xs text-gray-500">{{ codeLabel }}: {{ data.code }}</p>
    </div>

    <!-- Average Indice Score -->
    <div class="mb-6">
      <circular-score
        v-if="hasScore"
        :score="score"
        :max-score="10"
        :percentage="percentage"
        label="plantabilité"
        color-scheme="plantability"
        size="small"
      />
      <div v-else class="text-center text-gray-500 py-8">
        <p class="text-sm">Aucune donnée disponible</p>
      </div>
    </div>

    <!-- Plantability Distribution -->
    <plantability-distribution-chart
      v-if="plantabilityEntries.length > 0"
      :entries="plantabilityEntries"
      :show-legend="true"
      :show-details="false"
    />
  </div>
</template>
