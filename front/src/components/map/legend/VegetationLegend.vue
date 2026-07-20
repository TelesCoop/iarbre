<script lang="ts" setup>
import { computed } from "vue"
import { VegetationLegend, ELEVATION_GRADIENT_CSS, ELEVATION_LABEL_STOPS } from "@/utils/vegetation"
import { useMapStore } from "@/stores/map"
import FilterableLegendItem from "@/components/map/legend/FilterableLegendItem.vue"

const mapStore = useMapStore()

const showElevationLegend = computed(() => mapStore.showVegestrateHeight)
</script>

<template>
  <div class="flex flex-col items-center gap-1 lg:gap-2 font-sans" data-cy="vegetation-legend">
    <div class="legend-header">
      <span class="legend-title">{{
        showElevationLegend ? "Hauteur de végétation" : "Strate végétale"
      }}</span>
    </div>

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
      <div class="strate-list" role="list">
        <FilterableLegendItem
          v-for="item in VegetationLegend"
          :key="item.indice"
          :value="item.indice"
          :label="item.label"
          class="strate-item"
          :data-strate="item.indice"
          :title="item.label"
          role="listitem"
        >
          <span class="strate-swatch" :style="{ backgroundColor: item.color }"></span>
          <span class="strate-label">{{ item.label }}</span>
        </FilterableLegendItem>
      </div>
    </template>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.strate-list {
  @apply flex w-full max-w-56 flex-col gap-1;
}

.strate-item {
  @apply flex w-full items-center gap-2 cursor-pointer rounded-md px-2 py-1 text-left;
  @apply border-0 bg-transparent;
  @apply transition-colors duration-150 hover:bg-gray-50;
}

.strate-item.is-dimmed {
  @apply opacity-40;
}

.strate-swatch {
  @apply h-4 w-4 shrink-0 rounded-sm border border-gray-300;
}

.strate-item.is-selected .strate-swatch {
  @apply ring-2 ring-gray-600;
}

.strate-label {
  @apply text-xs text-gray-600 lg:text-sm;
}
</style>
