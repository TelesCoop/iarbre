<script setup lang="ts">
import MapComponent from "@/components/map/MapComponent.vue"
</script>

<template>
  <div class="map-container max-w-screen overflow-hidden relative">
    <map-component map-id="default" class="h-full" />
  </div>
</template>

<style scoped>
.map-container {
  height: var(--content-height);
}
</style>
