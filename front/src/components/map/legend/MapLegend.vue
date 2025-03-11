<script lang="ts" setup>
import PlantabilityLegend from "@/components/map/legend/PlantabilityLegend.vue"
import ClimateZonesLegend from "@/components/map/legend/ClimateZonesLegend.vue"
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"

const mapStore = useMapStore()
</script>

<template>
  <div class="z-3 absolute top-4 right-4 flex flex-col items-center card">
    <div class="font-accent text-base font-bold mb-2">
      {{ DataTypeToLabel[mapStore.selectedDataType] }}
    </div>
    <plantability-legend v-if="mapStore.selectedDataType === DataType.PLANTABILITY" />
    <climate-zones-legend v-else-if="mapStore.selectedDataType === DataType.LOCAL_CLIMATE_ZONES" />
  </div>
</template>
