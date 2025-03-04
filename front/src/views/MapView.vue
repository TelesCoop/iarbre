<script setup lang="ts">
import MapComponent from "@/components/map/MapComponent.vue"
</script>

<template>
  <div class="map-container max-full-height">
    <map-component map-id="default" class="h-100" />
    <a href="https://github.com/TelesCoop/iarbre" target="_blank" class="code-source-link"
      >code source</a
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
  bottom: 0.38rem
  left: 1.1rem
  color: $dark-green
  background-color: white
  padding: 0.25rem 0.5rem
  border-radius: 10px
  text-decoration: underline
  font-size: 0.8rem
</style>
