<script setup lang="ts">
import MapSidePanelHeader from "./MapSidePanelHeader.vue"
</script>

<template>
  <div
    class="absolute bg-white lg:flex top-0 left-0 flex-col z-1 w-[20rem] md:w-[24rem] lg:w-[26rem] xl:w-[30rem] 2xl:w-[32rem] max-w-[calc(100vw-0.5rem)]"
  >
    <map-side-panel-header />
    <div class="mx-5">
      <map-layer-switcher />
      <map-bg-switcher />
      <map-context-data
        class="max-h-[calc(100vh-6rem)] sm:max-h-[calc(100vh-7rem)] lg:max-h-[calc(100vh-6rem)] py-4!"
      />
    </div>
  </div>
</template>
