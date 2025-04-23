<script setup lang="ts">
import MapComponent from "@/components/map/MapComponent.vue"
import { useRouter, useRoute } from "vue-router"
import { ref } from "vue"
import type { MapParams } from "@/types"
import { DataType } from "@/utils/enum"

const router = useRouter()
const route = useRoute()

const mapParams = ref<MapParams>({
  dataType: DataType.PLANTABILITY,
  // Center to lyon Part-Dieu
  lng: 4.8537684279176645,
  lat: 45.75773479280862,
  zoom: 14
})
if (route.name === "mapWithUrlParams") {
  mapParams.value = {
    lng: parseFloat(route.params.lng as string),
    lat: parseFloat(route.params.lat as string),
    zoom: parseFloat(route.params.zoom as string),
    dataType: route.params.dataType as DataType
  }
}
</script>

<template>
  <div class="map-container max-w-screen overflow-hidden relative">
    <map-component
      map-id="default"
      :model-value="mapParams"
      @update:model-value="
        (params) => router.replace({ name: 'mapWithUrlParams', params: params as any })
      "
    />
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
