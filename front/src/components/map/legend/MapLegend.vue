<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"

const mapStore = useMapStore()
</script>

<template>
  <div v-if="mapStore.selectedDataType" class="map-legend">
    <div
      class="mb-2 text-sm font-semibold font-accent text-primary-900 text-center"
      data-cy="map-legend-title"
    >
      {{ DataTypeToLabel[mapStore.selectedDataType! as DataType] }}
    </div>
    <plantability-legend
      v-if="mapStore.selectedDataType === DataType.PLANTABILITY"
      class="w-full"
    />
    <climate-zone-legend
      v-else-if="mapStore.selectedDataType === DataType.CLIMATE_ZONE"
      class="w-full"
    />
    <vulnerability-legend
      v-else-if="mapStore.selectedDataType === DataType.VULNERABILITY"
      class="w-full"
    />
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";
.map-legend {
  @apply bg-white;
  display: flex;
  width: 221px;
  padding: 12px 10px 10px 10px;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 10px;
  border-radius: 10px;
}
</style>
