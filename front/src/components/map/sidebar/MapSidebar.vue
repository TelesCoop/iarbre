<template>
  <div class="map-sidebar">
    <div class="card">
      <layer-switcher />
    </div>
  </div>
</template>

<script setup lang="ts">
import LayerSwitcher from "@/components/map/sidebar/LayerSwitcher.vue"
</script>

<style lang="sass" scoped>
.map-sidebar
  position: absolute
  top: 0
  left: 0
  max-width: 18.75rem
  background-color: transparent
  padding: 1rem
</style>
