<script setup lang="ts">
import MapSidePanelHeader from "./MapSidePanelHeader.vue"
import MapSidePanelFooter from "./MapSidePanelFooter.vue"
</script>

<template>
  <div
    class="absolute bg-white lg:flex top-0 left-0 flex-col z-1 w-[20rem] md:w-[24rem] lg:w-[26rem] xl:w-[30rem] 2xl:w-[32rem] max-w-[calc(100vw-0.5rem)] h-full"
  >
    <map-side-panel-header />
    <div class="mx-5 flex-1 overflow-y-auto space-y-3 items-center">
      <map-bg-switcher />
      <map-layer-switcher />
      <map-context-data
        class="max-h-[calc(100vh-6rem)] sm:max-h-[calc(100vh-7rem)] lg:max-h-[calc(100vh-6rem)] py-4!"
      />
      <map-side-panel-footer />
    </div>
  </div>
</template>
