<script lang="ts" setup>
import PlantabilityLegend from "@/components/map/PlantabilityLegend.vue"
import ClimateZonesLegend from "@/components/map/ClimateZonesLegend.vue"
import { useMapStore } from "@/stores/map"
import { LAYERS } from "@/utils/enum"

const mapStore = useMapStore()
</script>

<template>
  <div class="map-legend card">
    <div class="legend-title">
      <template v-if="mapStore.selectedLayer === LAYERS.PLANTABILITY"> Plantabilité </template>
      <template v-else-if="mapStore.selectedLayer === LAYERS.LOCAL_CLIMATE_ZONES">
        Zones Climatiques Locales
      </template>
    </div>
    <plantability-legend v-if="mapStore.selectedLayer === LAYERS.PLANTABILITY" />
    <climate-zones-legend v-else-if="mapStore.selectedLayer === LAYERS.LOCAL_CLIMATE_ZONES" />
  </div>
</template>

<style lang="sass" scoped>
.map-legend
  z-index: 3
  position: absolute
  top: 1rem
  right: 1rem
  display: flex
  flex-direction: column
  align-items: center

  .legend-title
    font-family: $accent-font
    font-size: 1rem
    font-weight: bold
    margin-bottom: 0.5rem
</style>
