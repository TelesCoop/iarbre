<script lang="ts" setup>
import { computed } from "vue"
import DashboardWidgetCard from "@/components/dashboard/shared/DashboardWidgetCard.vue"
import DashboardBubbleChart from "@/components/dashboard/shared/DashboardBubbleChart.vue"
import type { DashboardLcz } from "@/types/dashboard"
import { VEGETATION_COLORS, SURFACE_COLORS } from "@/utils/dashboardColors"

interface Props {
  data: DashboardLcz
}

const props = defineProps<Props>()

const bubbles = computed(() => {
  const otherVeg = Math.max(props.data.totalVegetationRate - props.data.treeCoverRate, 0)
  return [
    {
      id: "trees",
      label: "Couvert arboré",
      value: props.data.treeCoverRate,
      color: VEGETATION_COLORS.trees
    },
    { id: "otherVeg", label: "Autre végétation", value: otherVeg, color: VEGETATION_COLORS.bushes },
    {
      id: "water",
      label: "Surface en eau",
      value: props.data.waterRate,
      color: SURFACE_COLORS.water
    }
  ]
})

function formatPct(v: number): string {
  return `${v.toFixed(1)}%`
}
</script>

<template>
  <DashboardWidgetCard subtitle="Couverture végétale et hydrique" title="Végétation et eau">
    <div class="widget-body">
      <DashboardBubbleChart :bubbles="bubbles" :formatter="formatPct" />
    </div>
  </DashboardWidgetCard>
</template>

<style scoped>
@reference "@/styles/main.css";

.widget-body {
  @apply flex-1 flex items-center justify-center w-full;
}
</style>
