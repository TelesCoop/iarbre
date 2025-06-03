<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"

const mapStore = useMapStore()
</script>

<template>
  <div class="map-legend">
    <div class="mb-2 text-sm font-semibold font-accent text-primary-900" data-cy="map-legend-title">
      {{ DataTypeToLabel[mapStore.selectedDataType! as DataType] }}
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
  @apply p-2 md:p-4;
  @apply top-0 right-0 mt-8 mr-2 lg:mr-8;
  @apply absolute z-3;
  @apply flex flex-col items-center;
  @apply rounded-md border-primary-500 border-0.5;
  @apply shadow-lg;
}
</style>
