<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { useAppStore } from "@/stores/app"
import { onMounted, onBeforeUnmount, ref, computed, type PropType } from "vue"
import { type MapDisplayState, type MapParams } from "@/types/map"
import ZoneDashboardCard from "@/components/map/ZoneDashboardCard.vue"

const props = defineProps({
  mapId: {
    required: true,
    type: String
  },
  initialDisplayState: {
    required: true,
    type: Object as PropType<MapDisplayState>
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

// Mirror the search bar and legend sizes onto CSS vars so the overlays placed
// below or beside them (shape toolbar card, street view) follow them.
const topRightControlsEl = ref<HTMLElement | null>(null)
const legendEl = ref<HTMLElement | null>(null)
const publishOverlaySizes = (topRight: HTMLElement | null, legend: HTMLElement | null) => {
  const root = document.documentElement.style
  root.setProperty("--top-right-controls-height", `${topRight?.offsetHeight ?? 0}px`)
  root.setProperty("--top-right-controls-width", `${topRight?.offsetWidth ?? 0}px`)
  root.setProperty("--legend-width", `${legend?.offsetWidth ?? 0}px`)
}
let overlaySizeObserver: ResizeObserver | null = null

onMounted(() => {
  mapStore.initMap(props.mapId, model.value.dataType!, props.initialDisplayState)
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

  const publishCurrentSizes = () => publishOverlaySizes(topRightControlsEl.value, legendEl.value)
  overlaySizeObserver = new ResizeObserver(publishCurrentSizes)
  for (const el of [topRightControlsEl.value, legendEl.value]) {
    if (el) overlaySizeObserver.observe(el)
  }
  publishCurrentSizes()
})

onBeforeUnmount(() => {
  overlaySizeObserver?.disconnect()
  publishOverlaySizes(null, null)
})

const isSidePanelVisible = computed(() => appStore.sidePanelVisible)
</script>

<template>
  <div class="block w-full h-full">
    <div :id="mapId" class="relative w-full h-full" data-cy="map-component"></div>
  </div>

  <div ref="topRightControlsEl" class="top-right-controls">
    <MapGeocoder />
  </div>

  <ShapeToolbar />
  <ShapeLiveChip />
  <ZoneDashboardCard />

  <div :class="['cadastre-info-container', { 'sidepanel-visible': isSidePanelVisible }]">
    <MapCadastreParcelInfo />
  </div>

  <div
    :class="['bottom-left-controls', { 'sidepanel-visible': isSidePanelVisible }]"
    data-cy="bottom-left-controls"
  >
    <MapBackgroundSelector />
    <MapLayerToggles v-if="appStore.isDesktop" />
  </div>

  <!-- Stacking these in one flex column keeps the gaps between items equal. -->
  <div ref="legendEl" :class="['legend-container', { 'sidepanel-visible': isSidePanelVisible }]">
    <MapLayerSwitcher
      v-if="appStore.isMobileOrTablet"
      :show-context-tools="false"
      :show-methodology="false"
      :with-border="false"
      data-cy="mobile-layer-switcher"
    />
    <MapLegend />
    <div class="legend-info-row">
      <MapResolution />
      <MapCoordinates />
    </div>
    <MapPanoramaxCredit />
    <MapCopyLinkButton />
  </div>

  <!-- After the legend: on mobile the street view spans the width and covers it. -->
  <div :class="['panoramax-viewer-container', { 'sidepanel-visible': isSidePanelVisible }]">
    <MapPanoramaxViewer />
  </div>
  <WelcomeMessage />
</template>

<style>
@reference "@/styles/main.css";

.top-right-controls {
  @apply absolute flex flex-col gap-2;
  z-index: var(--z-map-overlay);
  top: var(--map-edge-gap);
  right: var(--map-edge-gap);
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
  @apply absolute flex flex-col items-start pointer-events-none gap-2;
  @apply transition-all duration-300 ease-out;
  z-index: var(--z-map-overlay);
  top: var(--map-edge-gap);
  left: var(--map-edge-gap);
  width: calc(50% - 1rem);
}

.legend-container > * {
  @apply pointer-events-auto w-full;
}

@media (min-width: 1024px) {
  .legend-container {
    top: 0;
    @apply mt-2;
    display: grid;
    grid-template-columns: 1fr;
    width: auto;
  }

  .legend-container > * {
    @apply w-auto;
  }

  .legend-container.sidepanel-visible {
    left: calc(var(--width-sidepanel) + var(--map-edge-gap));
  }
}

.cadastre-info-container {
  @apply absolute pointer-events-none;
  @apply transition-all duration-300 ease-out;
  z-index: var(--z-map-overlay);
  left: 50%;
  transform: translateX(-50%);
  bottom: var(--map-above-bottom-row);
}

.cadastre-info-container > * {
  @apply pointer-events-auto;
}

@media (min-width: 1024px) {
  .cadastre-info-container.sidepanel-visible {
    left: calc(50% + var(--width-sidepanel) / 2);
  }
}

.panoramax-viewer-container {
  @apply absolute flex items-start justify-end pointer-events-none;
  z-index: var(--z-map-overlay);
  top: calc(var(--map-edge-gap) + var(--top-right-controls-height, 0px) + var(--map-edge-gap));
  right: var(--map-edge-gap);
  bottom: calc(var(--map-ctrl-offset) + var(--map-ctrl-stack-height) + var(--map-edge-gap));
  left: var(--map-edge-gap);
}

@media (min-width: 1024px) {
  .panoramax-viewer-container {
    left: calc(2 * var(--map-edge-gap) + var(--legend-width, 0px));
  }

  .panoramax-viewer-container.sidepanel-visible {
    left: calc(var(--width-sidepanel) + 2 * var(--map-edge-gap) + var(--legend-width, 0px));
  }
}

.panoramax-viewer-container > * {
  @apply pointer-events-auto;
}

.bottom-left-controls {
  @apply absolute flex flex-col items-start gap-2;
  @apply transition-all duration-300 ease-out;
  z-index: var(--z-map-overlay);
  left: var(--map-edge-gap);
  bottom: var(--map-overlay-bottom);
  /* Stops before the draw trigger, which shares the bottom row. */
  max-width: calc(100% - var(--map-trigger-right) - var(--map-ctrl-size) - 2 * var(--map-edge-gap));
}

@media (min-width: 1024px) {
  .bottom-left-controls {
    max-width: none;
  }

  .bottom-left-controls.sidepanel-visible {
    left: calc(var(--width-sidepanel) + var(--map-edge-gap));
  }
}

.legend-info-row {
  @apply flex flex-row items-center gap-2 pointer-events-auto w-full;
  min-width: 0;
  overflow: hidden;
}
</style>
