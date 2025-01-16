<template>
  <div class="map-plantabilitie-legend">
    <PlantabiliteLegend />
  </div>
</template>

<script lang="ts" setup>
import PlantabiliteLegend from "@/components/map/PlantabiliteLegend.vue"
</script>

<style lang="sass" scoped>
.map-plantabilitie-legend
  z-index: 3
  position: absolute
  top: 5rem
  right: 3rem
  background-color: white
  border-radius: 10px
  box-shadow: 4px 4px 5px rgba(0, 0, 0, 0.3)
  padding: 0.75rem 0.5rem
</style>
