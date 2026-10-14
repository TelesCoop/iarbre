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
      <button
        v-for="(item, index) in mapStore.selectedLayer.legend"
        :key="item.label"
        type="button"
        class="flex items-center gap-2 select-none cursor-pointer text-left"
        :class="{ 'opacity-40 line-through': mapStore.hiddenClasses.includes(index) }"
        :aria-pressed="!mapStore.hiddenClasses.includes(index)"
        @click="mapStore.toggleClass(index)"
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
      </button>
    </div>

    <p class="legend-attribution">Source : {{ mapStore.selectedLayer.attribution }}</p>
  </div>
</template>
