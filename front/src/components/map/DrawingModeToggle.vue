<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import Button from "primevue/button"

const mapStore = useMapStore()
</script>

<template>
  <div class="bg-white rounded-lg overflow-hidden">
    <Button
      :class="[
        'w-10 h-10 p-0 flex items-center justify-center transition-colors drawing-mode-btn',
        { active: mapStore.isToolbarVisible }
      ]"
      data-cy="drawing-mode-toggle"
      severity="secondary"
      size="small"
      @click="mapStore.toggleToolbar()"
    >
      <img :src="`/icons/map-draw.svg`" alt="Mode dessin" class="w-6 h-6 drawing-mode-icon" />
    </Button>
  </div>
</template>

<style scoped></style>
