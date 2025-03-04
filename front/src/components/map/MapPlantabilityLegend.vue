<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import PlantabilityLegend from "@/components/map/PlantabilityLegend.vue"

const mapStore = useMapStore()
</script>

<template>
  <div class="map-plantability-legend">
    <div v-if="mapStore.visibleLayers.length === 0" class="no-layers-message">
      No visible layers
    </div>
    <div v-for="layer in mapStore.visibleLayers" v-else :key="layer.modelType" class="legend-item">
      <h4 class="legend-title">{{ layer.title }}</h4>
      <plantability-legend v-if="layer.modelType === 'tile'" />
      <!-- Add other legend types here as needed -->
    </div>
  </div>
</template>

<style lang="sass" scoped>
.map-plantability-legend
  z-index: 3
  position: absolute
  top: 1rem
  right: 1rem
  background-color: white
  border-radius: 10px
  box-shadow: 4px 4px 5px rgba(0, 0, 0, 0.3)
  padding: 0.75rem 1.5rem
  max-width: 300px

  .no-layers-message
    font-family: $accent-font
    font-size: 0.9rem
    text-align: center
    padding: 0.5rem 0

  .legend-item
    margin-bottom: 1rem

    &:last-child
      margin-bottom: 0

    .legend-title
      font-family: $accent-font
      font-size: 1rem
      margin: 0 0 0.5rem 0
      text-align: center
      color: #333
</style>
