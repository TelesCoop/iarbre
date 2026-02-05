<script lang="ts" setup>
import MapComponent from "@/components/map/MapComponent.vue"
import SidebarComponent from "@/components/sidebar/SidebarComponent.vue"
import { useRouter, useRoute } from "vue-router"
import { ref } from "vue"
import type { MapParams } from "@/types/map"
import { DataType } from "@/utils/enum"
import { DEFAULT_MAP_PARAMS } from "@/utils/constants"

const router = useRouter()
const route = useRoute()

const mapParams = ref<MapParams>({ ...DEFAULT_MAP_PARAMS })
const hasAlreadyChanged = ref<boolean>(false)

if (route.name === "mapWithUrlParams") {
  mapParams.value = {
    lng: parseFloat(route.params.lng as string),
    lat: parseFloat(route.params.lat as string),
    zoom: parseFloat(route.params.zoom as string),
    dataType: route.params.dataType as DataType
  }
}

const handleMapUpdate = (params: MapParams) => {
  const replaceUrl = () => {
    router.replace({
      name: "mapWithUrlParams",
      params: {
        ...params,
        lat: params.lat.toFixed(5),
        lng: params.lng.toFixed(5)
      } as any
    })
  }

  if (hasAlreadyChanged.value) {
    replaceUrl()
    return
  }

  const hasChanged = Object.keys(DEFAULT_MAP_PARAMS).some(
    (key) => params[key as keyof MapParams] !== DEFAULT_MAP_PARAMS[key as keyof MapParams]
  )

  if (hasChanged) {
    hasAlreadyChanged.value = true
    replaceUrl()
  }
}
</script>

<template>
  <div class="map-view-wrapper">
    <SidebarComponent />
    <MapSidePanel />
    <div class="map-container max-w-screen overflow-hidden relative">
      <MapComponent
        :model-value="mapParams"
        map-id="default"
        @update:model-value="handleMapUpdate"
      />

      <!-- Drawer -->
      <MapConfigDrawer />
      <MapScoresDrawer />
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.map-view-wrapper {
  @apply flex;
  height: 100vh;
  height: 100dvh;
  margin-left: 0;
}

@media (min-width: 1024px) {
  .map-view-wrapper {
    margin-left: 64px;
  }
}

.map-container {
  @apply flex-1;
  height: 100vh;
  height: 100dvh;
}
</style>
