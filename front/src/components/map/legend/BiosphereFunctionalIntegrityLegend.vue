<script lang="ts" setup>
import { BiosphereIntegrityLegend } from "@/utils/biosphere_functional_integrity"
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()

const handleClick = (name: string) => {
  mapStore.toggleAndApplyFilter(name)
}
</script>

<template>
  <div class="flex flex-col items-start gap-2 font-sans" data-cy="biosphere-integrity-legend">
    <div class="legend-header">
      <span class="legend-title">Part d'espaces naturels dans le km² voisin</span>
    </div>
    <div
      v-for="(color, name, index) in BiosphereIntegrityLegend"
      :key="index"
      class="legend-item"
      :class="{ 'opacity-40': mapStore.hasActiveFilters && !mapStore.isFiltered(name) }"
      @click="handleClick(name)"
    >
      <div
        class="legend-swatch"
        :class="{ 'ring-2 ring-offset-1 ring-gray-600': mapStore.isFiltered(name) }"
        :style="{ backgroundColor: color }"
      ></div>
      <span class="legend-item-label">{{ name }}</span>
    </div>
  </div>
</template>
