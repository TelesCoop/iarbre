<script lang="ts" setup>
import { computed } from "vue"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import DashboardBubbleChart from "@/components/dashboard/shared/DashboardBubbleChart.vue"
import type { DashboardVegetation } from "@/types/dashboard"
import { VEGETATION_COLORS } from "@/utils/dashboardColors"

interface Props {
  data: DashboardVegetation
}

const props = defineProps<Props>()

const hasData = computed(() => props.data.totalHa >= 1)

const totalDisplay = computed(() => {
  const ha = props.data.totalHa
  if (ha >= 1000) return `${(ha / 1000).toFixed(1)} km²`
  return `${ha.toFixed(0)} ha`
})

const bubbles = computed(() => [
  {
    id: "trees",
    label: "Arborée",
    value: props.data.treesSurfaceHa,
    color: VEGETATION_COLORS.trees
  },
  {
    id: "bushes",
    label: "Arbustive",
    value: props.data.bushesSurfaceHa,
    color: VEGETATION_COLORS.bushes
  },
  {
    id: "grass",
    label: "Herbacée",
    value: props.data.grassSurfaceHa,
    color: VEGETATION_COLORS.grass
  }
])

function formatHa(ha: number): string {
  if (ha >= 1000) return `${(ha / 1000).toFixed(1)} km²`
  return `${ha.toFixed(0)} ha`
}
</script>

<template>
  <DashboardWidgetCard subtitle="Surfaces de végétation par strate" title="Végétation existante">
    <div v-if="hasData" class="widget-body">
      <div class="total-display">
        <span class="total-value">{{ totalDisplay }}</span>
        <span class="total-label">de végétation totale</span>
      </div>
      <div class="chart-container">
        <DashboardBubbleChart :bubbles="bubbles" :formatter="formatHa" />
      </div>
    </div>
    <div v-else class="widget-empty">
      <span class="empty-text">Données indisponibles</span>
    </div>
  </DashboardWidgetCard>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-body {
  @apply flex-1 flex items-center justify-center gap-3 w-full;
}

.total-display {
  @apply flex flex-col items-center;
}

.total-value {
  @apply text-2xl md:text-3xl font-bold text-primary-700;
}

.total-label {
  @apply text-xs text-gray-500;
}

.chart-container {
  @apply flex-1 self-stretch;
}

.widget-empty {
  @apply flex-1 flex items-center justify-center;
}

.empty-text {
  @apply text-sm text-gray-400;
}
</style>
