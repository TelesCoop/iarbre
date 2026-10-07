<script lang="ts" setup>
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()
</script>

<template>
  <div class="legend-panel">
    <div
      class="font-accent flex flex-col items-start justify-center text-xs leading-4 gap-2 px-2 py-1 w-full"
      data-cy="raster-legend"
    >
      <div
        v-for="item in mapStore.selectedLayer.legend"
        :key="item.label"
        class="flex items-center gap-2 select-none"
      >
        <div
          class="w-4 h-4 shrink-0 border border-gray-300 rounded-sm"
          :style="{ backgroundColor: item.color }"
        ></div>
        <span class="text-sm text-primary-900">
          {{ item.label }}
          <span v-if="item.detail" class="hidden lg:inline text-xs text-gray-500"
            >({{ item.detail }})</span
          >
        </span>
      </div>
    </div>

    <p class="legend-attribution">Source : {{ mapStore.selectedLayer.attribution }}</p>
  </div>
</template>
