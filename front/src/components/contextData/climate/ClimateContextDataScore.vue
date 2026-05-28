<script lang="ts" setup>
import { computed } from "vue"
import type { ClimateData } from "@/types/climate"
import { getContrastTextHex } from "@/utils/color"
import { CLIMATE_ZONE_COLOR } from "@/utils/climateZone"

interface ClimateScoreProps {
  data: ClimateData
}

const props = defineProps<ClimateScoreProps>()

const zoneColor = computed(() => CLIMATE_ZONE_COLOR[props.data?.lczIndex] || "#D1D5DB")

const zoneTextColor = computed(() => getContrastTextHex(zoneColor.value))

const zoneLabel = computed(() => props.data?.lczIndex || "-")

const zoneDescription = computed(() => props.data?.lczDescription || "Description non disponible")
</script>

<template>
  <section class="climate-score-card" data-cy="climate-context-data-score">
    <span
      class="zone-swatch"
      :style="{ backgroundColor: zoneColor, color: zoneTextColor }"
      aria-hidden="true"
    >
      {{ zoneLabel }}
    </span>
    <span class="zone-copy">
      <span class="zone-eyebrow">Zone climatique locale</span>
      <span class="zone-title">{{ zoneDescription }}</span>
    </span>
  </section>
</template>

<style scoped>
@reference "@/styles/main.css";

.climate-score-card {
  @apply flex w-72 max-w-full items-center gap-3 rounded-xl border border-gray-200 bg-gray-50 px-4 py-3;
  @apply min-h-20;
}

.zone-swatch {
  @apply flex h-12 w-12 shrink-0 items-center justify-center rounded-lg;
  @apply text-lg font-bold tabular-nums;
}

.zone-copy {
  @apply flex min-w-0 flex-col text-left;
}

.zone-eyebrow {
  @apply text-xs font-medium text-gray-500;
}

.zone-title {
  @apply line-clamp-3 text-sm font-semibold leading-snug text-gray-900;
  overflow-wrap: anywhere;
}
</style>
