<script lang="ts" setup>
import MapComponent from "@/components/map/MapComponent.vue"
import SidebarComponent from "@/components/sidebar/SidebarComponent.vue"
import { useRouter, useRoute } from "vue-router"
import { computed, ref, watch } from "vue"
import type { MapParams } from "@/types/map"
import { DataType } from "@/utils/enum"
import { DEFAULT_MAP_PARAMS } from "@/utils/constants"
import { buildMapDisplayQuery, parseMapDisplayState } from "@/utils/mapUrlState"
import { useMapStore } from "@/stores/map"

const router = useRouter()
const route = useRoute()
const mapStore = useMapStore()

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

const initialDisplayState = parseMapDisplayState(route.query, mapParams.value.dataType)

const lastKnownParams = ref<MapParams>({ ...mapParams.value })

const displayQuery = computed(() =>
  buildMapDisplayQuery({
    filters: mapStore.filteredValues,
    mapStyle: mapStore.selectedMapStyle,
    overlayLayers: mapStore.visibleOverlayLayers
  })
)

const replaceUrl = () => {
  router.replace({
    name: "mapWithUrlParams",
    params: {
      ...lastKnownParams.value,
      lat: lastKnownParams.value.lat.toFixed(5),
      lng: lastKnownParams.value.lng.toFixed(5)
    } as any,
    query: displayQuery.value
  })
}

const handleMapUpdate = (params: MapParams) => {
  lastKnownParams.value = params

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

// Compared by value: restoring an identical display must leave the URL untouched.
watch(
  () => JSON.stringify(displayQuery.value),
  () => {
    hasAlreadyChanged.value = true
    replaceUrl()
  }
)
</script>

<template>
  <div class="map-view-wrapper">
    <SidebarComponent />
    <MapSidePanel />
    <div class="map-container max-w-screen overflow-hidden relative">
      <MapComponent
        :model-value="mapParams"
        :initial-display-state="initialDisplayState"
        map-id="default"
        @update:model-value="handleMapUpdate"
      />

      <MapScoresDrawer />
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.map-view-wrapper {
  @apply flex;
  height: calc(100vh - var(--feedback-banner-height, 0px));
  height: calc(100dvh - var(--feedback-banner-height, 0px));
  margin-left: 0;
}

@media (min-width: 1024px) {
  .map-view-wrapper {
    margin-left: 4.5rem;
  }
}

.map-container {
  @apply flex-1;
  height: 100%;
}
</style>
