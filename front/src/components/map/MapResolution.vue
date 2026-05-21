<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { useAppStore } from "@/stores/app"
import { ZoomToGridSize } from "@/utils/plantability"

const mapStore = useMapStore()
const appStore = useAppStore()

const gridSize = computed(() => {
  const zoom = Math.floor(mapStore.currentZoom)
  return ZoomToGridSize[zoom] ?? null
})

const isVisible = computed(
  () =>
    appStore.isDesktop && mapStore.selectedDataType === "plantability" && gridSize.value !== null
)
</script>

<template>
  <div v-if="isVisible" class="resolution-info">
    <div class="resolution-label">Résolution</div>
    <div class="resolution-value">
      <div class="tile-pixel"></div>
      <span class="resolution-number">{{ gridSize }}</span>
      <span class="resolution-unit">m</span>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.resolution-info {
  @apply flex flex-row items-center gap-2.5 py-1.5 px-2.5 bg-white border border-gray-200 rounded-lg pointer-events-auto font-sans shrink-0;
}

.resolution-label {
  @apply text-xs font-medium text-gray-500 uppercase tracking-tight;
}

.resolution-value {
  @apply flex items-center gap-1;
}

.tile-pixel {
  @apply w-3 h-3 bg-scale-8 rounded-sm shrink-0;
}

.resolution-number {
  @apply text-sm font-bold text-gray-800 leading-none tabular-nums;
}

.resolution-unit {
  @apply text-xs font-medium text-gray-500;
}
</style>
