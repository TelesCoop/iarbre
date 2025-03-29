<script setup lang="ts">
import MapComponent from "@/components/map/MapComponent.vue"
</script>

<template>
  <div class="map-container max-w-screen overflow-hidden relative">
    <map-component map-id="default" class="h-full" />
    <a
      href="https://github.com/TelesCoop/iarbre"
      target="_blank"
      class="absolute bottom-[0.38rem] left-[1.1rem] text-brown bg-off-white px-2 py-1 rounded-[10px] underline text-[0.8rem]"
    >
      code source</a
    >
  </div>
</template>

<style scoped>
.map-container {
  height: var(--content-height);
}
</style>
