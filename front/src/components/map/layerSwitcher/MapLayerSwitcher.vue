<script setup lang="ts">
import LayerSwitcher from "@/components/map/layerSwitcher/LayerSwitcher.vue"
</script>

<template>
  <div
    class="absolute top-0 left-0 max-w-[18.75rem] bg-transparent p-4"
    data-cy="map-layer-switcher"
  >
    <div class="card">
      <layer-switcher />
    </div>
  </div>
</template>
