<script lang="ts" setup>
import PlantabilityLegend from "@/components/map/legend/PlantabilityLegend.vue"
import ClimateZonesLegend from "@/components/map/legend/ClimateZonesLegend.vue"
import VulnerabilityLegend from "@/components/map/legend/VulnerabilityLegend.vue"
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"

const mapStore = useMapStore()
</script>

<template>
  <div class="map-legend">
    <div class="mb-2 text-sm font-semibold font-accent text-primary-900" data-cy="map-legend-title">
      {{ DataTypeToLabel[mapStore.selectedDataType] }}
    </div>
    <plantability-legend v-if="mapStore.selectedDataType === DataType.PLANTABILITY" />
    <climate-zones-legend v-else-if="mapStore.selectedDataType === DataType.LOCAL_CLIMATE_ZONES" />
    <vulnerability-legend v-else-if="mapStore.selectedDataType === DataType.VULNERABILITY" />
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";
.map-legend {
  @apply bg-white;
  @apply p-3;
  @apply absolute z-3;
  @apply max-lg:bottom-18 max-lg:left-4 lg:top-4 lg:right-4;
  @apply flex flex-col items-center;
  @apply rounded-md border-primary-500 border-1;
  @apply shadow-lg;
}
</style>
