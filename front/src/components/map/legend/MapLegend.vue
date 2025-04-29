<script lang="ts" setup>
import PlantabilityLegend from "@/components/map/legend/PlantabilityLegend.vue"
import ClimateZonesLegend from "@/components/map/legend/ClimateZonesLegend.vue"
import VulnerabilityLegend from "@/components/map/legend/VulnerabilityLegend.vue"
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"

const mapStore = useMapStore()
</script>

<template>
  <div
    class="z-3 absolute max-lg:bottom-18 max-lg:left-4 lg:top-4 lg:right-4 flex flex-col items-center bg-white p-3 rounded-md border-primary-500 border-1 shadow-lg"
  >
    <div class="mb-2 text-sm font-semibold font-accent text-primary-900" data-cy="map-legend-title">
      {{ DataTypeToLabel[mapStore.selectedDataType] }}
    </div>
    <plantability-legend v-if="mapStore.selectedDataType === DataType.PLANTABILITY" />
    <climate-zones-legend v-else-if="mapStore.selectedDataType === DataType.LOCAL_CLIMATE_ZONES" />
    <vulnerability-legend v-else-if="mapStore.selectedDataType === DataType.VULNERABILITY" />
  </div>
</template>
