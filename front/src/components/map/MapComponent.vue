<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { useAppStore } from "@/stores/app"
import { onMounted, type PropType, computed } from "vue"
import { type MapParams } from "@/types/map"
import { ZoomToGridSize } from "@/utils/plantability"
import LayerSwitcher from "@/components/layerSwitcher/LayerSwitcher.vue"

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

const isSidePanelVisible = computed(() => appStore.sidePanelVisible)
</script>

<template>
  <div class="block w-full h-full">
    <div :id="mapId" class="relative w-full h-full" data-cy="map-component"></div>
  </div>

  <!-- Top-right controls stack -->
  <div class="top-right-controls">
    <MapCoordinates />
    <MapGeocoder />
  </div>

  <!-- Drawing controls positioned to the left of maplibre controls -->
  <div class="drawing-controls-container">
    <DrawingModeToggle />
  </div>
  <div v-if="mapStore.isToolbarVisible" class="selection-toolbar-container">
    <SelectionModeToolbar />
  </div>

  <!-- Drawing controls - only visible in shape mode -->
  <DrawingControls />

  <!-- Background selector in bottom-left corner -->
  <div :class="['bg-selector-container', { 'sidepanel-visible': isSidePanelVisible }]">
    <MapBackgroundSelector />
  </div>

  <!-- Legend and controls - top left -->
  <div :class="['legend-container', { 'sidepanel-visible': isSidePanelVisible }]">
    <LayerSwitcher v-if="appStore.isMobileOrTablet" />
    <MapLegend />
    <div
      v-if="appStore.isDesktop && mapStore.selectedDataType === 'plantability' && gridSize"
      class="grid-size-info"
    >
      <div class="grid-size-label">Résolution</div>
      <div class="grid-size-value">
        <div class="tile-pixel"></div>
        <span class="grid-size-number">{{ gridSize }}</span>
        <span class="grid-size-unit">m</span>
      </div>
    </div>
    <MapFiltersStatus v-if="appStore.isDesktop" />
  </div>
  <WelcomeMessage />
</template>

<style>
@reference "@/styles/main.css";

.top-right-controls {
  @apply absolute right-2 top-2 flex flex-col gap-2 z-50;
  width: calc(50% - 1rem);
}

.top-right-controls > * {
  @apply w-full;
}

@media (min-width: 1024px) {
  .top-right-controls {
    width: auto;
  }

  .top-right-controls > * {
    @apply w-auto;
  }
}

.legend-container {
  @apply absolute flex flex-col items-start pointer-events-none z-30 gap-2 top-0 mt-2;
  @apply transition-all duration-300 ease-out;
  left: 0.5rem;
  width: calc(50% - 1rem);
}

.legend-container > * {
  @apply pointer-events-auto w-full;
}

@media (min-width: 1024px) {
  .legend-container {
    width: auto;
  }

  .legend-container > * {
    @apply w-auto;
  }

  .legend-container.sidepanel-visible {
    left: calc(var(--width-sidepanel) + 0.5rem);
  }
}

.bg-selector-container {
  @apply absolute z-30;
  @apply transition-all duration-300 ease-out;
  left: 0.5rem;
  bottom: 64px;
}

@media (min-width: 1024px) {
  .bg-selector-container {
    bottom: 0.5rem;
  }

  .bg-selector-container.sidepanel-visible {
    left: calc(var(--width-sidepanel) + 0.5rem);
  }
}

.grid-size-info {
  @apply flex flex-row items-center gap-2.5 py-2 px-3 bg-white border border-gray-200 rounded-lg pointer-events-auto font-sans;
}

.grid-size-label {
  @apply text-xs font-medium text-gray-500 uppercase tracking-tight;
}

.grid-size-value {
  @apply flex items-center gap-1;
}

.tile-pixel {
  @apply w-3 h-3 bg-scale-8 rounded-sm shrink-0;
}

.grid-size-number {
  @apply text-base font-bold text-gray-800 leading-none tabular-nums;
}

.grid-size-unit {
  @apply text-xs font-medium text-gray-500;
}

/* Drawing controls - aligned with maplibre 3D button */
.drawing-controls-container {
  @apply absolute z-30;
  bottom: 130px;
  right: 68px;
}

.selection-toolbar-container {
  @apply absolute z-30;
  bottom: 180px;
  right: 68px;
}

@media (min-width: 1024px) {
  .drawing-controls-container {
    bottom: 18px;
    right: 68px;
  }

  .selection-toolbar-container {
    bottom: 18px;
    right: 116px;
  }
}
</style>
