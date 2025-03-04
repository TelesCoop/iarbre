<script setup lang="ts">
import MapComponent from "@/components/map/MapComponent.vue"
</script>

<template>
  <div class="map-container max-full-height">
    <map-component map-id="default" class="h-100" />
    <a href="https://github.com/TelesCoop/iarbre" target="_blank" class="code-source-link"
      >code_source</a
    >
  </div>
</template>

<style scoped lang="sass">
.map-container
  max-width: 100vw
  height:  $content-height
  overflow: hidden
  position: relative

.code-source-link
  position: absolute
  bottom: 1rem
  left: 1.1rem
  color: black
  text-decoration: underline
  font-size: 1.2rem
  font-weight: bold
  background-color: rgba(239, 239, 237, 0.6)  // Semi-transparent $off-white
  padding: 0.2rem 0.5rem
  border-radius: 5px
</style>
