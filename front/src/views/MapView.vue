<script lang="ts" setup>
import MapComponent from "@/components/map/MapComponent.vue"
import { useRouter, useRoute } from "vue-router"
import { ref } from "vue"
import type { MapParams } from "@/types/map"
import { DataType } from "@/utils/enum"
import { DEFAULT_MAP_CENTER } from "@/utils/constants"

const router = useRouter()
const route = useRoute()

const mapParams = ref<MapParams>({
  dataType: DataType.PLANTABILITY,
  lng: DEFAULT_MAP_CENTER.lng,
  lat: DEFAULT_MAP_CENTER.lat,
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
      :model-value="mapParams"
      map-id="default"
      @update:model-value="
        (params) => router.replace({ name: 'mapWithUrlParams', params: params as any })
      "
    />

    <!-- Drawer -->
    <map-config-drawer />
    <map-scores-drawer />
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";
.map-container {
  height: var(--content-height);
}
</style>
