<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { useAppStore } from "@/stores/app"
import { onMounted, type PropType, computed } from "vue"
import { type MapParams } from "@/types/map"
import { ZoomToGridSize } from "@/utils/plantability"

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

const gridSize = computed(() => {
  const zoom = Math.floor(mapStore.currentZoom)
  return ZoomToGridSize[zoom] ?? null
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

  <!-- Top-right controls stack -->
  <div class="absolute right-0 top-0 mt-2 mr-2 flex flex-col gap-2" style="z-index: 50">
    <map-coordinates />
    <map-geocoder />
  </div>

  <!-- Drawing controls in bottom-right corner -->
  <div class="absolute bottom-2 z-40 flex flex-col-reverse gap-2" style="right: 56px">
    <drawing-mode-toggle />
    <selection-mode-toolbar v-if="mapStore.isToolbarVisible" />
  </div>

  <!-- Drawing controls - only visible in shape mode -->
  <drawing-controls />

<!-- Background selector in bottom-left corner -->
  <div class="absolute bottom-2 left-2 z-40 hidden lg:block">
    <map-background-selector />
  </div>

  <div v-if="appStore.isDesktop" class="legend-container flex">
    <map-legend />
    <div v-if="mapStore.selectedDataType === 'plantability' && gridSize" class="grid-size-info">
      <div class="flex items-center gap-2">
        <div class="tile-pixel"></div>
        <span>{{ gridSize }}m</span>
      </div>
    </div>
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
  @apply absolute flex flex-col items-start pointer-events-none z-30 gap-2 left-2 top-0 mx-1 mt-2;
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

.grid-size-info {
  @apply text-sm text-center font-sans font-bold;
  @apply bg-white px-3 py-2 rounded-lg border border-gray-200;
  @apply pointer-events-auto;
}

.tile-pixel {
  width: 12px;
  height: 12px;
  background-color: #a6d5a3;
  border-radius: 2px;
  flex-shrink: 0;
}
</style>
