<script lang="ts" setup>
import { computed } from "vue"
import {
  VegetationLegend,
  ELEVATION_GRADIENT_CSS,
  ELEVATION_LABEL_STOPS,
  formatHeightRange,
  heightRangeColor
} from "@/utils/vegetation"
import { useMapStore } from "@/stores/map"
import FilterableLegendItem from "@/components/map/legend/FilterableLegendItem.vue"
import LegendItem from "@/components/map/legend/LegendItem.vue"

const mapStore = useMapStore()

const showElevationLegend = computed(() => mapStore.showVegestrateHeight)

const heightRanges = computed(() =>
  mapStore.vegestrateHeightRanges.map((range) => ({
    label: formatHeightRange(range),
    color: heightRangeColor(range)
  }))
)
</script>

<template>
  <div class="flex flex-col items-center gap-1 lg:gap-2 font-sans" data-cy="vegetation-legend">
    <div class="legend-header">
      <span class="legend-title">{{
        showElevationLegend ? "Hauteur de végétation" : "Strate végétale"
      }}</span>
    </div>

    <template v-if="showElevationLegend">
      <div v-if="heightRanges.length" class="strate-list" role="list">
        <div
          v-for="range in heightRanges"
          :key="range.label"
          class="strate-item"
          role="listitem"
          :title="range.label"
        >
          <LegendItem :label="range.label" :color="range.color" />
        </div>
      </div>
      <div v-else class="flex flex-col gap-1 w-full select-none">
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
    <div v-else class="strate-list" role="list">
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
        <LegendItem :label="item.label" :color="item.color" />
      </FilterableLegendItem>
    </div>
  </div>
</template>
