<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"

const mapStore = useMapStore()
</script>

<template>
  <div
    v-if="mapStore.selectedDataType"
    class="bg-white flex px-4 py-2 flex-col justify-center items-center gap-2 rounded-lg"
  >
    <div
      class="hidden lg:block text-sm font-semibold font-accent text-primary-900 text-center"
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
    <plant-vulnerability-legend
      v-else-if="mapStore.selectedDataType === DataType.PLANTABILITY_VULNERABILITY"
      class="w-full"
    />
    <biosphere-functional-integrity-legend
      v-else-if="mapStore.selectedDataType === DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY"
      class="w-full"
    />
    <vegetation-legend
      v-else-if="mapStore.selectedDataType === DataType.VEGETATION"
      class="w-full"
    />
  </div>
</template>
