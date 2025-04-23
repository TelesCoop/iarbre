<script lang="ts" setup>
import MapComponent from "@/components/map/MapComponent.vue"
</script>

<template>
  <div class="map-container max-w-screen overflow-hidden relative">
    <map-component class="h-full" map-id="default" />
    <Button
      as="a"
      class="absolute bottom-[7%] left-[1%] z-10 underline"
      href="https://github.com/TelesCoop/iarbre"
      icon="pi pi-github"
      label="Code source"
      severity="primary"
      target="_blank"
    >
    </Button>
  </div>
</template>

<style scoped>
.map-container {
  height: var(--content-height);
}
</style>
