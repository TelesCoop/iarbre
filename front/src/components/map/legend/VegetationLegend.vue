<script lang="ts" setup>
import { computed } from "vue"
import {
  VegetationLegend,
  isElevationMode,
  ELEVATION_GRADIENT_CSS,
  ELEVATION_LABEL_STOPS
} from "@/utils/vegetation"
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()

const showElevationLegend = computed(() => isElevationMode(mapStore.vegestrateMode))

const handleStrateClick = (indice: string) => {
  mapStore.toggleAndApplyFilter(indice)
}
</script>

<template>
  <div
    class="font-accent flex flex-col items-start justify-center text-xs leading-4 gap-2 px-2 py-1"
    data-cy="biosphere-integrity-legend"
  >
    <template v-if="showElevationLegend">
      <div class="flex flex-col gap-1 w-full select-none">
        <div
          class="h-4 rounded-sm border border-gray-300 w-full"
          :style="{ background: ELEVATION_GRADIENT_CSS }"
        ></div>
        <div class="relative h-4 text-xs text-primary-900">
          <span
            v-for="(stop, i) in ELEVATION_LABEL_STOPS"
            :key="stop.label"
            class="absolute"
            :style="
              i === 0
                ? 'left:0'
                : i === ELEVATION_LABEL_STOPS.length - 1
                  ? 'right:0'
                  : `left:${stop.position}%;transform:translateX(-50%)`
            "
            >{{ stop.label }}</span
          >
        </div>
      </div>
    </template>
    <template v-else>
      <div
        v-for="item in VegetationLegend"
        :key="item.indice"
        class="flex items-center gap-2 cursor-pointer select-none transition-opacity duration-150"
        :class="{ 'opacity-40': mapStore.hasActiveFilters && !mapStore.isFiltered(item.indice) }"
        @click="handleStrateClick(item.indice)"
      >
        <div
          class="w-4 h-4 border border-gray-300 rounded-sm"
          :class="{ 'ring-2 ring-offset-1 ring-gray-600': mapStore.isFiltered(item.indice) }"
          :style="{ backgroundColor: item.color }"
        ></div>
        <span class="text-sm text-primary-900">{{ item.label }}</span>
      </div>
    </template>
  </div>
</template>
