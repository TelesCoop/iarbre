<script lang="ts" setup>
import { computed } from "vue"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import DashboardArcScore from "@/components/dashboard/shared/DashboardArcScore.vue"
import DashboardDetailBars from "@/components/dashboard/shared/DashboardDetailBars.vue"
import AppBadge from "@/components/shared/AppBadge.vue"
import type { DashboardLcz } from "@/types/dashboard"
import { SURFACE_COLORS } from "@/utils/dashboardColors"

interface Props {
  data: DashboardLcz
}

const props = defineProps<Props>()

const impermeableRate = computed(
  () =>
    Math.round(((props.data.buildingRate ?? 0) + (props.data.impermeableSurfaceRate ?? 0)) * 10) /
    10
)

const permeableRate = computed(() => Math.round((100 - impermeableRate.value) * 10) / 10)

const impermeablePercent = computed(() => Math.round(impermeableRate.value))
const permeablePercent = computed(() => 100 - impermeablePercent.value)

const accentColor = computed(() => {
  if (impermeableRate.value > 70) return "#EF4444"
  if (impermeableRate.value > 50) return "#F59E0B"
  return "#6B7280"
})

const details = computed(() => [
  { label: "Bâti", value: props.data.buildingRate, color: SURFACE_COLORS.building },
  {
    label: "Routes / minéral",
    value: props.data.impermeableSurfaceRate,
    color: SURFACE_COLORS.impermeable
  },
  {
    label: "Sol perméable",
    value: props.data.permeableSoilRate,
    color: SURFACE_COLORS.permeableSoil
  },
  { label: "Végétation", value: props.data.totalVegetationRate, color: SURFACE_COLORS.vegetation },
  { label: "Eau", value: props.data.waterRate, color: SURFACE_COLORS.water }
])
</script>

<template>
  <DashboardWidgetCard subtitle="Taux d'imperméabilisation des sols" title="Perméabilité">
    <div class="widget-body">
      <DashboardArcScore
        :color="accentColor"
        :max-value="100"
        :value="impermeableRate"
        :secondary-color="SURFACE_COLORS.vegetation"
      >
        <div class="arc-dual">
          <span class="arc-rate impermeable">{{ impermeablePercent }}%</span>
          <span class="arc-rate-label">imperméable</span>
          <span class="arc-rate permeable">{{ permeablePercent }}%</span>
          <span class="arc-rate-label">perméable</span>
        </div>
      </DashboardArcScore>

      <div class="detail-row">
        <div class="stacked-bar">
          <div :style="{ width: `${permeableRate}%` }" class="stacked-fill stacked-permeable" />
          <div :style="{ width: `${impermeableRate}%` }" class="stacked-fill stacked-impermeable" />
        </div>
        <div class="detail-header">
          <AppBadge variant="success">{{ permeablePercent }}% perméable</AppBadge>
          <AppBadge variant="secondary">{{ impermeablePercent }}% imperméable</AppBadge>
        </div>
        <DashboardDetailBars :items="details" />
      </div>
    </div>
  </DashboardWidgetCard>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-body {
  @apply flex-1 flex flex-col items-center justify-center gap-4 w-full;
}

.arc-dual {
  @apply flex flex-col items-center;
}

.arc-rate {
  @apply text-sm font-bold leading-tight;
}

.arc-rate.impermeable {
  @apply text-gray-700;
}

.arc-rate.permeable {
  @apply text-green-600;
}

.arc-rate-label {
  @apply text-[10px] text-gray-400 leading-tight;
}

.detail-row {
  @apply flex flex-col gap-3 w-full;
}

.stacked-bar {
  @apply flex w-full h-3 rounded-full overflow-hidden;
}

.stacked-fill {
  @apply h-full;
  animation: barGrow 700ms ease-out both;
}

.stacked-permeable {
  background-color: #55b250;
}

.stacked-impermeable {
  background-color: #6b7280;
}

.detail-header {
  @apply flex items-center justify-center gap-3;
}

@keyframes barGrow {
  from {
    width: 0 !important;
  }
}
</style>
