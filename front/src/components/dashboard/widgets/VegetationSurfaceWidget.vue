<script lang="ts" setup>
import { computed } from "vue"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import type { DashboardVegetation } from "@/types/dashboard"
import { VEGETATION_COLORS } from "@/utils/dashboardColors"
import { getContrastTextHex } from "@/utils/color"

interface Props {
  data: DashboardVegetation
}

const props = defineProps<Props>()

const KM2_IN_M2 = 1_000_000

const hasData = computed(() => props.data.totalM2 >= 1)

const useKm2 = computed(() => props.data.totalM2 >= KM2_IN_M2)

const formatSurface = (m2: number) => {
  if (useKm2.value) {
    return `${(m2 / KM2_IN_M2).toLocaleString("fr-FR", { maximumFractionDigits: 2 })} km²`
  }
  return `${Math.round(m2).toLocaleString("fr-FR")} m²`
}

const items = computed(() => {
  const entries = [
    { label: "🖼️ TOTALE", value: props.data.totalM2, color: "#426a45" },
    {
      label: "🌳 HAUTE",
      value: props.data.treesSurfaceM2,
      color: VEGETATION_COLORS.trees
    },
    {
      label: "🌿 MOYENNE",
      value: props.data.bushesSurfaceM2,
      color: VEGETATION_COLORS.bushes
    },
    { label: "🌱 BASSE", value: props.data.grassSurfaceM2, color: VEGETATION_COLORS.grass }
  ]
  return entries.map((e) => ({
    ...e,
    textColor: getContrastTextHex(e.color),
    pct: props.data.totalM2 > 0 ? Math.min((e.value / props.data.totalM2) * 100, 100) : 0,
    display: formatSurface(e.value)
  }))
})
</script>

<template>
  <DashboardWidgetCard
    :subtitle="`Découpage en trois strates : haute (>1.5m), moyenne (<1.5m) et pelouses.`"
    title="Inventaire stratifié de végétation existante"
  >
    <div v-if="hasData" class="widget-body">
      <div v-for="item in items" :key="item.label" class="bar-item">
        <span class="bar-label">{{ item.label }}</span>
        <div class="bar-track">
          <div
            class="bar-fill"
            :style="{
              width: `${item.pct}%`,
              backgroundColor: item.color
            }"
          >
            <span class="bar-inner-value" :style="{ color: item.textColor }">{{
              item.display
            }}</span>
          </div>
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
  @apply flex flex-col gap-4 flex-1 w-full justify-center;
}

.bar-item {
  @apply flex flex-col gap-1.5;
}

.bar-label {
  @apply text-xs text-gray-500 uppercase tracking-wide;
}

.bar-track {
  @apply w-full h-9 bg-gray-100 rounded-md overflow-hidden;
}

.bar-fill {
  @apply h-full rounded-md flex items-center px-2;
  animation: barGrow 700ms ease-out both;
}

.bar-inner-value {
  @apply text-sm font-bold whitespace-nowrap;
}

@keyframes barGrow {
  from {
    width: 0 !important;
  }
}
</style>
