<script lang="ts" setup>
import { VegetationLegend } from "@/utils/vegetation"
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()

const handleStrateClick = (indice: string) => {
  mapStore.toggleAndApplyFilter(indice)
}
</script>

<template>
  <div class="flex flex-col items-start gap-2 font-sans" data-cy="vegetation-legend">
    <div class="legend-header">
      <span class="legend-title">Strate végétale</span>
    </div>
    <div
      v-for="item in VegetationLegend"
      :key="item.indice"
      class="legend-item"
      :class="{ 'opacity-40': mapStore.hasActiveFilters && !mapStore.isFiltered(item.indice) }"
      @click="handleStrateClick(item.indice)"
    >
      <div
        class="legend-swatch"
        :class="{ 'ring-2 ring-offset-1 ring-gray-600': mapStore.isFiltered(item.indice) }"
        :style="{ backgroundColor: item.color }"
      ></div>
      <span class="legend-item-label">{{ item.label }}</span>
    </div>
  </div>
</template>
