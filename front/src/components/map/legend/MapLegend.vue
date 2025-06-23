<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"

const mapStore = useMapStore()
defineProps<{
  isMinify?: boolean
}>()
</script>

<template>
  <div v-if="mapStore.selectedDataType" class="map-legend">
    <div
      v-if="!isMinify"
      class="mb-2 text-sm font-semibold font-accent text-primary-900"
      data-cy="map-legend-title"
    >
      {{ DataTypeToLabel[mapStore.selectedDataType! as DataType] }}
    </div>
    <plantability-legend
      v-if="mapStore.selectedDataType === DataType.PLANTABILITY"
      :is-minify="isMinify"
    />
    <climate-zone-legend
      v-else-if="mapStore.selectedDataType === DataType.CLIMATE_ZONE"
      :is-minify="isMinify"
    />
    <vulnerability-legend
      v-else-if="mapStore.selectedDataType === DataType.VULNERABILITY"
      :is-minify="isMinify"
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
