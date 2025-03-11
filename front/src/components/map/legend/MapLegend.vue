<script lang="ts" setup>
import PlantabilityLegend from "@/components/map/legend/PlantabilityLegend.vue"
import ClimateZonesLegend from "@/components/map/legend/ClimateZonesLegend.vue"
import { useMapStore } from "@/stores/map"
import { LAYERS } from "@/utils/enum"

const mapStore = useMapStore()
</script>

<template>
  <div class="z-3 absolute top-4 right-4 flex flex-col items-center card">
    <div class="font-accent text-base font-bold mb-2">
      <template v-if="mapStore.selectedLayer === LAYERS.PLANTABILITY"> Plantabilité </template>
      <template v-else-if="mapStore.selectedLayer === LAYERS.LOCAL_CLIMATE_ZONES">
        Zones Climatiques Locales
      </template>
    </div>
    <plantability-legend v-if="mapStore.selectedLayer === LAYERS.PLANTABILITY" />
    <climate-zones-legend v-else-if="mapStore.selectedLayer === LAYERS.LOCAL_CLIMATE_ZONES" />
  </div>
</template>
