<script lang="ts" setup>
import MapComponent from "@/components/map/MapComponent.vue"
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
    router.replace({ name: "mapWithUrlParams", params: params as any })
  }

  // If already changed once, always update URL
  if (hasAlreadyChanged.value) {
    replaceUrl()
    return
  }

  // Check if params differ from defaults
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
  <div class="map-container max-w-screen overflow-hidden relative">
    <map-component
      :model-value="mapParams"
      map-id="default"
      @update:model-value="handleMapUpdate"
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
