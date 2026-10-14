<script lang="ts" setup>
import { computed } from "vue"
import {
  BIOSPHERE_DETAIL_ZOOM,
  BIOSPHERE_CLASSES,
  BIOSPHERE_DETAIL_CLASSES
} from "@/utils/biosphere_functional_integrity"
import FilterableLegendItem from "@/components/map/legend/FilterableLegendItem.vue"
import FilterIndicator from "@/components/map/legend/FilterIndicator.vue"
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()

const classes = computed(() =>
  mapStore.currentZoom >= BIOSPHERE_DETAIL_ZOOM ? BIOSPHERE_DETAIL_CLASSES : BIOSPHERE_CLASSES
)
</script>

<template>
  <div
    class="flex flex-col items-center gap-1 lg:gap-2 font-sans"
    data-cy="biosphere-integrity-legend"
  >
    <div class="legend-header">
      <span class="legend-title">Intégrité fonctionnelle de la biosphère</span>
    </div>
    <div class="legend-content pb-3">
      <div class="legend-label">
        <span class="legend-axis-indicator">−</span>
        <span class="legend-axis-text">Artificialisé</span>
      </div>
      <div class="relative">
        <div class="legend-scale">
          <FilterableLegendItem
            v-for="({ label: name, color }, index) in classes"
            :key="name"
            :value="name"
            :label="name"
            :class="[
              'relative shrink-0 cursor-pointer border-0 p-0 w-2.5 h-4.5 lg:w-3.75 lg:h-6.75 transition-transform duration-150 hover:scale-y-110 [&.is-selected]:z-10 [&.is-selected]:border-2 [&.is-selected]:border-primary-900 [&.is-dimmed]:opacity-40',
              index === 0 ? 'rounded-l' : '',
              index === classes.length - 1 ? 'rounded-r' : ''
            ]"
            :data-biosphere="name"
            :style="{ backgroundColor: color }"
            :title="name"
          >
            <FilterIndicator :is-visible="mapStore.isFiltered(name)" />
          </FilterableLegendItem>
        </div>
        <div
          class="absolute inset-x-0 top-full mt-0.5 flex justify-between text-2xs font-medium text-gray-500"
        >
          <span>0 %</span>
          <span>100 %</span>
        </div>
      </div>
      <div class="legend-label">
        <span class="legend-axis-text">Naturel</span>
        <span class="legend-axis-indicator">+</span>
      </div>
    </div>
  </div>
</template>
