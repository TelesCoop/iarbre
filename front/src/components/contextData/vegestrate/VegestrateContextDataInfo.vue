<script lang="ts" setup>
import { computed } from "vue"
import type { VegetationData } from "@/types/vegetation"
import { getZoneDesc, getZoneColor } from "@/utils/vegetation"

interface VegetationContextDataInfoProps {
  data: VegetationData
}

const props = defineProps<VegetationContextDataInfoProps>()

const strateLabel = computed(() => getZoneDesc(props.data.indice))
const strateColor = computed(() => getZoneColor(props.data.indice))

const formattedSurface = computed(() => {
  return props.data.surface.toLocaleString("fr-FR", { maximumFractionDigits: 2 })
})
</script>

<template>
  <div class="strate-info">
    <div class="strate-type">
      <div class="strate-swatch" :style="{ backgroundColor: strateColor }" :title="strateLabel" />
      <span class="strate-label">{{ strateLabel }}</span>
    </div>
    <div class="strate-surface">
      <span class="surface-label">Surface</span>
      <span class="surface-value">
        {{ formattedSurface }}
        <span class="surface-unit">m²</span>
      </span>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.strate-info {
  @apply flex flex-col gap-3;
}

.strate-type {
  @apply flex items-center justify-center gap-3 p-3 bg-gray-50 rounded-lg;
}

.strate-swatch {
  @apply w-5 h-5 rounded shrink-0;
}

.strate-label {
  @apply text-sm font-semibold text-gray-800;
}

.strate-surface {
  @apply flex items-center justify-between px-3 py-2 rounded-lg border border-gray-200;
}

.surface-label {
  @apply text-sm text-gray-600;
}

.surface-value {
  @apply text-sm font-semibold text-gray-800;
}

.surface-unit {
  @apply text-xs font-normal text-gray-500 ml-0.5;
}
</style>
