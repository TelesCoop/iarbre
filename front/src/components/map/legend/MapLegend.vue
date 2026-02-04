<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"

const mapStore = useMapStore()
</script>

<template>
  <div v-if="mapStore.selectedDataType" class="legend-panel">
    <PlantabilityLegend v-if="mapStore.selectedDataType === DataType.PLANTABILITY" class="w-full" />
    <ClimateZoneLegend
      v-else-if="mapStore.selectedDataType === DataType.CLIMATE_ZONE"
      class="w-full"
    />
    <VulnerabilityLegend
      v-else-if="mapStore.selectedDataType === DataType.VULNERABILITY"
      class="w-full"
    />
    <PlantVulnerabilityLegend
      v-else-if="mapStore.selectedDataType === DataType.PLANTABILITY_VULNERABILITY"
      class="w-full"
    />
    <vegetation-legend
      v-else-if="mapStore.selectedDataType === DataType.VEGETATION"
      class="w-full"
    />
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.legend-panel {
  @apply flex flex-col justify-center items-center gap-2 p-3 bg-white border border-gray-200 rounded-lg;
}
</style>
