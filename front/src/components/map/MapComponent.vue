<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { useAppStore } from "@/stores/app"
import { onMounted, type PropType } from "vue"
import { type MapParams } from "@/types/map"

const props = defineProps({
  mapId: {
    required: true,
    type: String
  }
})

const model = defineModel<MapParams>({
  required: true,
  type: Object as PropType<MapParams>
})

const emit = defineEmits<{
  (e: "update:modelValue", value: MapParams): void
}>()

const mapStore = useMapStore()
const appStore = useAppStore()

onMounted(() => {
  mapStore.initMap(props.mapId, model.value.dataType!)
  const mapInstance = mapStore.getMapInstance(props.mapId)

  mapInstance.jumpTo({
    center: [model.value.lng, model.value.lat],
    zoom: model.value.zoom
  })

  const updateParams = () => {
    const params: MapParams = {
      zoom: Math.round(mapStore.currentZoom),
      lat: Math.round(100000 * mapInstance.getCenter().lat) / 100000,
      lng: Math.round(100000 * mapInstance.getCenter().lng) / 100000,
      dataType: mapStore.selectedDataType
    }
    emit("update:modelValue", params)
  }

  mapInstance.on("moveend", updateParams)
  updateParams()
})
</script>

<template>
  <div class="block w-full h-full lg:flex">
    <map-side-panel v-if="appStore.isDesktop" />
    <div
      :id="mapId"
      class="relative w-screen h-full lg:ml-auto lg:w-screen-without-sidepanel"
      data-cy="map-component"
    ></div>
  </div>
  <div v-if="appStore.isMobileOrTablet" class="absolute left-0 top-0 mt-2 ml-2">
    <map-config-drawer-toggle />
  </div>

  <!-- Drawing mode toggle - visible on all screens -->
  <div class="absolute right-0 top-0 mt-2 mr-2 z-40">
    <drawing-mode-toggle />
  </div>

  <!-- Selection mode toolbar - only visible when toolbar is toggled -->
  <div v-if="mapStore.isToolbarVisible" class="absolute right-0 top-14 mt-2 mr-2 z-40">
    <selection-mode-toolbar />
  </div>

  <!-- Drawing controls - only visible in shape mode -->
  <drawing-controls />

  <div v-if="appStore.isDesktop" class="legend-container flex">
    <map-legend />
    <map-filters-status />
  </div>
  <div v-else class="flex items-center justify-center">
    <map-context-data-mobile />
  </div>
  <welcome-message />
</template>

<style>
@reference "@/styles/main.css";

.legend-container {
  @apply absolute flex flex-col items-start pointer-events-none z-30 gap-2 left-105 top-0 mx-1 mt-4;
}

.legend-container > * {
  pointer-events: auto;
  flex: 1;
  width: 100%;
}

@media (min-width: 1024px) {
  .legend-container {
    margin-right: 2rem;
  }
}

.maplibregl-ctrl-geocoder {
  width: 90%;
  max-width: 400px;
}

.maplibregl-ctrl-geocoder--suggestions {
  width: 100%;
}
.maplibregl-ctrl-geocoder.maplibregl-ctrl-geocoder--collapsed,
.maplibregl-ctrl-geocoder.maplibregl-ctrl-geocoder--collapsed .maplibregl-ctrl-geocoder--input {
  width: 30px;
  min-width: 30px;
  height: 30px;
}
.maplibregl-ctrl-geocoder.maplibregl-ctrl-geocoder--collapsed .maplibregl-ctrl-geocoder--icon {
  width: 25px;
  height: 25px;
  top: 3px;
  left: 3px;
}

.maplibregl-ctrl-geocoder--input {
  @apply text-primary-500;
  @apply font-accent;
}

.maplibregl-ctrl-geocoder--icon-search {
  @apply fill-primary-500;
}
</style>
