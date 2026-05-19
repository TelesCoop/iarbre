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
    color: BUILDING_WIDGET_COLORS.surface,
    display: `${props.lcz.averageBuildingSurfaceRate.toFixed(1)} %`
  },
  {
    label: "Hauteur moyenne",
    value: props.lcz.averageBuildingHeight,
    max: 50,
    color: BUILDING_WIDGET_COLORS.height,
    display: `${props.lcz.averageBuildingHeight.toFixed(1)} m`
  },
  {
    label: "Superficie moyenne",
    value: props.buildings.averageBuildingFootprintM2,
    max: 500,
    color: BUILDING_WIDGET_COLORS.footprint,
    display: `${Math.round(props.buildings.averageBuildingFootprintM2)} m²`
  }
])
</script>

<template>
  <DashboardWidgetCard subtitle="Indicateurs moyens sur les bâtiments">
    <template #title>
      Caractéristiques du bâti (<a
        href="https://www.data.gouv.fr/datasets/bd-topo-r"
        target="_blank"
        rel="noopener noreferrer"
        >BD Topo</a
      >)
    </template>
    <div class="widget-body">
      <div v-for="bar in bars" :key="bar.label" class="bar-item">
        <span class="bar-label">{{ bar.label }}</span>
        <div class="bar-track">
          <div
            class="bar-fill"
            :style="{
              width: `${Math.min((bar.value / bar.max) * 100, 100)}%`,
              backgroundColor: bar.color
            }"
          >
            <span class="bar-inner-value">{{ bar.display }}</span>
          </div>
        </div>
      </div>
    </div>
  </DashboardWidgetCard>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-body {
  @apply flex flex-col gap-5 justify-center;
}

.bar-item {
  @apply flex flex-col gap-1.5;
}

.bar-label {
  @apply text-xs text-gray-500 uppercase tracking-wide;
}

.bar-track {
  @apply w-full h-11 bg-gray-100 rounded-lg overflow-hidden;
}

.bar-fill {
  @apply h-full rounded-lg flex items-center px-3;
  animation: barGrow 700ms ease-out both;
}

.bar-inner-value {
  @apply text-sm font-bold text-white whitespace-nowrap;
}

@keyframes barGrow {
  from {
    width: 0 !important;
  }
}
</style>
