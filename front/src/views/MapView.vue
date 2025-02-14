<script setup lang="ts">
import MapComponent from "@/components/map/MapComponent.vue"
</script>

<template>
  <div class="map-container max-full-height">
    <map-component map-id="default" class="h-100" />
  </div>
</template>

<style scoped lang="sass">
.map-container
  max-width: 100vw
  height:  $content-height
  overflow: hidden
  position: relative
</style>
