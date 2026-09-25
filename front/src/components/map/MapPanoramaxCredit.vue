<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { PANORAMAX_HOME_URL } from "@/utils/panoramax"

const mapStore = useMapStore()
</script>

<template>
  <p
    v-if="mapStore.showPanoramaxLayer"
    class="map-control w-full py-1 px-2 text-center text-xs font-sans text-gray-500"
    data-cy="panoramax-credit"
  >
    Images : ©
    <a class="underline" :href="PANORAMAX_HOME_URL" rel="noopener" target="_blank">Panoramax</a>
  </p>
</template>
