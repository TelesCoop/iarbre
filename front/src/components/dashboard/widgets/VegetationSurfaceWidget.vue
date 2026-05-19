<script lang="ts" setup>
import { computed } from "vue"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import type { DashboardVegetation } from "@/types/dashboard"
import { VEGETATION_COLORS } from "@/utils/dashboardColors"

interface Props {
  data: DashboardVegetation
}

const props = defineProps<Props>()

const hasData = computed(() => props.data.totalHa >= 1)

const totalDisplay = computed(() => {
  const ha = props.data.totalHa
  if (ha >= 100) return `${(ha / 100).toFixed(1)} km²`
  return `${ha.toFixed(0)} ha`
})

const strates = computed(() => [
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

const total = computed(() => strates.value.reduce((s, x) => s + x.value, 0))

function formatHa(ha: number): string {
  if (ha >= 100) return `${(ha / 100).toFixed(1)} km²`
  return `${ha.toFixed(0)} ha`
}

function pct(val: number): number {
  return total.value > 0 ? (val / total.value) * 100 : 0
}
</script>

<template>
  <DashboardWidgetCard subtitle="Répartition par strate" title="Surfaces de végétation">
    <div v-if="hasData" class="widget-body">
      <div class="total-display">
        <span class="total-value">{{ totalDisplay }}</span>
        <span class="total-label">de végétation totale</span>
      </div>

      <div class="stacked-bar">
        <div
          v-for="s in strates"
          :key="s.id"
          class="stacked-segment"
          :style="{ width: `${pct(s.value)}%`, backgroundColor: s.color }"
        />
      </div>

      <div class="legend">
        <div v-for="s in strates" :key="s.id" class="legend-row">
          <span class="legend-dot" :style="{ backgroundColor: s.color }" />
          <span class="legend-label">{{ s.label }}</span>
          <span class="legend-value">{{ formatHa(s.value) }}</span>
          <span class="legend-pct">{{ pct(s.value).toFixed(0) }}%</span>
        </div>
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
  @apply flex-1 flex flex-col gap-4 w-full;
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

.stacked-bar {
  @apply flex w-full h-5 rounded-full overflow-hidden gap-0.5;
}

.stacked-segment {
  @apply h-full first:rounded-l-full last:rounded-r-full;
  animation: segGrow 700ms ease-out both;
}

.legend {
  @apply flex flex-col gap-2;
}

.legend-row {
  @apply flex items-center gap-2 text-xs;
}

.legend-dot {
  @apply w-2.5 h-2.5 rounded-full shrink-0;
}

.legend-label {
  @apply text-gray-500 flex-1;
}

.legend-value {
  @apply font-semibold text-gray-700 tabular-nums;
}

.legend-pct {
  @apply text-gray-400 tabular-nums w-8 text-right;
}

.widget-empty {
  @apply flex-1 flex items-center justify-center;
}

.empty-text {
  @apply text-sm text-gray-400;
}

@keyframes segGrow {
  from {
    width: 0 !important;
  }
}
</style>
