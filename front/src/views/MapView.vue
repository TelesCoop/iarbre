<script lang="ts" setup>
import MapComponent from "@/components/map/MapComponent.vue"
</script>

<template>
  <div class="map-container max-w-screen overflow-hidden relative">
    <map-component class="h-full" map-id="default" />
  </div>
</template>

<style scoped>
.map-container {
  height: var(--content-height);
}
</style>
