<script lang="ts" setup>
import { computed } from "vue"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import type { DashboardBuildings, DashboardLcz } from "@/types/dashboard"
import { BUILDING_WIDGET_COLORS } from "@/utils/dashboardColors"

interface Props {
  lcz: DashboardLcz
  buildings: DashboardBuildings
}

const props = defineProps<Props>()

const bars = computed(() => [
  {
    label: "Taux de surface bâtie",
    value: props.lcz.averageBuildingSurfaceRate,
    max: 100,
    unit: "%",
    color: BUILDING_WIDGET_COLORS.surface,
    display: `${props.lcz.averageBuildingSurfaceRate.toFixed(1)} %`
  },
  {
    label: "Hauteur moyenne",
    value: props.lcz.averageBuildingHeight,
    max: 50,
    unit: "m",
    color: BUILDING_WIDGET_COLORS.height,
    display: `${props.lcz.averageBuildingHeight.toFixed(1)} m`
  },
  {
    label: "Superficie moyenne",
    value: props.buildings.averageBuildingFootprintM2,
    max: 5000,
    unit: "m²",
    color: BUILDING_WIDGET_COLORS.footprint,
    display: `${Math.round(props.buildings.averageBuildingFootprintM2)} m²`
  }
])
</script>

<template>
  <DashboardWidgetCard
    subtitle="Indicateurs moyens sur les bâtiments"
    title="Caractéristiques du bâti (d'après la BD Topo)"
  >
    <div class="widget-body">
      <div v-for="bar in bars" :key="bar.label" class="bar-item">
        <div class="bar-header">
          <span class="bar-dot" :style="{ backgroundColor: bar.color }" />
          <span class="bar-label">{{ bar.label }}</span>
          <span class="bar-value">{{ bar.display }}</span>
        </div>
        <div class="bar-track">
          <div
            class="bar-fill"
            :style="{
              width: `${Math.min((bar.value / bar.max) * 100, 100)}%`,
              backgroundColor: bar.color
            }"
          />
        </div>
      </div>
    </div>
  </DashboardWidgetCard>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-body {
  @apply flex-1 flex flex-col gap-5 w-full justify-center;
}

.bar-item {
  @apply flex flex-col gap-1.5;
}

.bar-header {
  @apply flex items-center gap-2 text-xs;
}

.bar-dot {
  @apply w-2 h-2 rounded-full shrink-0;
}

.bar-label {
  @apply text-gray-500 flex-1;
}

.bar-value {
  @apply font-semibold text-gray-700 tabular-nums;
}

.bar-track {
  @apply w-full h-2 bg-gray-100 rounded-full overflow-hidden;
}

.bar-fill {
  @apply h-full rounded-full;
  animation: barGrow 700ms ease-out both;
}

@keyframes barGrow {
  from {
    width: 0 !important;
  }
}
</style>
