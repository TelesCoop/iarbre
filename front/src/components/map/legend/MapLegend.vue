<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"

const mapStore = useMapStore()
</script>

<template>
  <div v-if="mapStore.selectedDataType" class="map-legend">
    <div class="mb-2 text-sm font-semibold font-accent text-primary-900" data-cy="map-legend-title">
      {{ DataTypeToLabel[mapStore.selectedDataType! as DataType] }}
    </div>
    <plantability-legend v-if="mapStore.selectedDataType === DataType.PLANTABILITY" />
    <climate-zone-legend v-else-if="mapStore.selectedDataType === DataType.CLIMATE_ZONE" />
    <vulnerability-legend v-else-if="mapStore.selectedDataType === DataType.VULNERABILITY" />
    <mix-plantability-vulnerability-legend
      v-else-if="mapStore.selectedDataType === DataType.MIX_PLANTABILITY_AND_VULNERABILITY"
    />
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";
.map-legend {
  @apply bg-white;
  @apply p-2 md:p-4;
  @apply top-0 right-0;
  @apply flex flex-col items-center;
  @apply rounded-md border-primary-500 border-0.5;
}
</style>
