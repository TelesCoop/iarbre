<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"
import { computed } from "vue"

const mapStore = useMapStore()

const selectedDataTypesArray = computed(() => Array.from(mapStore.selectedDataTypes))
const isMultipleLayersSelected = computed(() => mapStore.selectedDataTypes.size > 1)
</script>

<template>
  <div class="map-legend">
    <template v-if="!isMultipleLayersSelected">
      <div
        class="mb-2 text-sm font-semibold font-accent text-primary-900"
        data-cy="map-legend-title"
      >
        {{ DataTypeToLabel[mapStore.selectedDataType! as DataType] }}
      </div>
      <plantability-legend v-if="mapStore.selectedDataType === DataType.PLANTABILITY" />
      <climate-zones-legend
        v-else-if="mapStore.selectedDataType === DataType.LOCAL_CLIMATE_ZONES"
      />
      <vulnerability-legend v-else-if="mapStore.selectedDataType === DataType.VULNERABILITY" />
    </template>

    <template v-else>
      <div
        class="mb-2 text-sm font-semibold font-accent text-primary-900"
        data-cy="map-legend-title"
      >
        Calques actifs ({{ mapStore.selectedDataTypes.size }})
      </div>
      <div class="space-y-3">
        <div
          v-for="dataType in selectedDataTypesArray"
          :key="dataType"
          class="border-l-4 border-primary-500 pl-2"
        >
          <div class="text-xs font-medium mb-1">
            {{ DataTypeToLabel[dataType] }}
          </div>
          <plantability-legend v-if="dataType === DataType.PLANTABILITY" />
          <climate-zones-legend v-else-if="dataType === DataType.LOCAL_CLIMATE_ZONES" />
          <vulnerability-legend v-else-if="dataType === DataType.VULNERABILITY" />
        </div>
      </div>
    </template>
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
  @apply shadow-lg;
}
</style>
