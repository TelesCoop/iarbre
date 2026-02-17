<script lang="ts" setup>
import { computed } from "vue"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import DashboardArcScore from "@/components/dashboard/shared/DashboardArcScore.vue"
import type { DashboardLcz } from "@/types/dashboard"

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

const accentColor = computed(() => {
  if (impermeableRate.value > 70) return "#EF4444"
  if (impermeableRate.value > 50) return "#F59E0B"
  return "#6B7280"
})

const details = computed(() => [
  { label: "Bâti", value: props.data.buildingRate, color: "#F59E0B" },
  { label: "Routes / minéral", value: props.data.impermeableSurfaceRate, color: "#6B7280" },
  { label: "Sol perméable", value: props.data.permeableSoilRate, color: "#D4A853" },
  { label: "Végétation", value: props.data.totalVegetationRate, color: "#55B250" },
  { label: "Eau", value: props.data.waterRate, color: "#3B82F6" }
])
</script>

<template>
  <DashboardWidgetCard subtitle="Taux d'imperméabilisation des sols" title="Perméabilité">
    <div class="widget-body">
      <DashboardArcScore
        :color="accentColor"
        :display-value="`${impermeableRate.toFixed(0)}%`"
        :max-value="100"
        :value="impermeableRate"
        label="imperméable"
      />

      <div class="detail-row">
        <div class="detail-header">
          <span class="detail-badge permeable">{{ permeableRate.toFixed(0) }}% perméable</span>
          <span class="detail-badge impermeable"
            >{{ impermeableRate.toFixed(0) }}% imperméable</span
          >
        </div>
        <div class="detail-bars">
          <div v-for="item in details" :key="item.label" class="detail-item">
            <div class="detail-label-row">
              <span class="detail-dot" :style="{ backgroundColor: item.color }" />
              <span class="detail-label">{{ item.label }}</span>
              <span class="detail-value">{{ item.value.toFixed(1) }}%</span>
            </div>
            <div class="bar-track">
              <div
                class="bar-fill"
                :style="{ width: `${item.value}%`, backgroundColor: item.color }"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </DashboardWidgetCard>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-body {
  @apply flex flex-col items-center gap-4 w-full;
}

.detail-row {
  @apply flex flex-col gap-3 w-full;
}

.detail-header {
  @apply flex items-center justify-center gap-3;
}

.detail-badge {
  @apply text-xs font-medium px-2 py-0.5 rounded-full;
}

.detail-badge.permeable {
  @apply bg-green-50 text-green-700;
}

.detail-badge.impermeable {
  @apply bg-gray-100 text-gray-600;
}

.detail-bars {
  @apply flex flex-col gap-2.5;
}

.detail-item {
  @apply flex flex-col gap-1;
}

.detail-label-row {
  @apply flex items-center gap-2 text-xs;
}

.detail-dot {
  @apply w-2 h-2 rounded-full shrink-0;
}

.detail-label {
  @apply text-gray-500;
}

.detail-value {
  @apply font-semibold text-gray-700 ml-auto tabular-nums;
}

.bar-track {
  @apply w-full h-1.5 bg-gray-100 rounded-full overflow-hidden;
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
