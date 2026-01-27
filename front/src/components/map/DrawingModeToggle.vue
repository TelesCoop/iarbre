<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import Button from "primevue/button"

const mapStore = useMapStore()
</script>

<template>
  <div class="bg-white rounded-lg shadow-md overflow-hidden">
    <Button
      data-cy="drawing-mode-toggle"
      size="small"
      :severity="mapStore.isToolbarVisible ? 'primary' : 'secondary'"
      class="w-10 h-10 p-0 flex items-center justify-center rounded-none! border-0!"
      @click="mapStore.toggleToolbar()"
    >
      <img
        :src="`/icons/map-draw${mapStore.isToolbarVisible ? '-white' : ''}.svg`"
        alt="Mode dessin"
        class="w-6 h-6"
      />
    </Button>
  </div>
</template>
