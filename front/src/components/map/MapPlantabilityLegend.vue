<script lang="ts" setup>
import PlantabilityLegend from "@/components/map/PlantabilityLegend.vue"
</script>

<template>
  <div class="map-plantability-legend">
    <plantability-legend />
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
  padding: 0.75rem 2.5rem
</style>
