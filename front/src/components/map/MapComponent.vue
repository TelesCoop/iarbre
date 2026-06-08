<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { useAppStore } from "@/stores/app"
import { onMounted, onBeforeUnmount, ref, computed, type PropType } from "vue"
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

// The bottom-left stack has a content-driven width (background selector + layer
// toggles). Publish it so the centered shape card can keep itself centered in
// the band between this stack and the draw trigger, in pure CSS.
const bottomLeftControlsEl = ref<HTMLElement | null>(null)
const CONTROLS_WIDTH_VAR = "--bottom-left-controls-width"
const setControlsWidth = (px: number) =>
  document.documentElement.style.setProperty(CONTROLS_WIDTH_VAR, `${px}px`)
let controlsObserver: ResizeObserver | null = null

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

  if (bottomLeftControlsEl.value) {
    controlsObserver = new ResizeObserver(() =>
      setControlsWidth(bottomLeftControlsEl.value?.offsetWidth ?? 0)
    )
    controlsObserver.observe(bottomLeftControlsEl.value)
    setControlsWidth(bottomLeftControlsEl.value.offsetWidth)
  }
})

onBeforeUnmount(() => {
  controlsObserver?.disconnect()
  setControlsWidth(0)
})

const isSidePanelVisible = computed(() => appStore.sidePanelVisible)
</script>

<template>
  <div class="block w-full h-full">
    <div :id="mapId" class="relative w-full h-full" data-cy="map-component"></div>
  </div>

  <!-- Top-right controls stack -->
  <div class="top-right-controls">
    <MapGeocoder />
  </div>

  <!-- Unified shape selection toolbar + live readout chip -->
  <ShapeToolbar />
  <ShapeLiveChip />

  <!-- Cadastre parcel info - bottom center -->
  <div :class="['cadastre-info-container', { 'sidepanel-visible': isSidePanelVisible }]">
    <MapCadastreParcelInfo />
  </div>

  <!-- Bottom-left stack: background selector + layer toggles (desktop only) -->
  <div
    ref="bottomLeftControlsEl"
    :class="['bottom-left-controls', { 'sidepanel-visible': isSidePanelVisible }]"
    data-cy="bottom-left-controls"
  >
    <MapBackgroundSelector />
    <MapLayerToggles v-if="appStore.isDesktop" />
  </div>

  <!-- Top-left stack: mobile layer switcher (mobile only), legend, then info row.
       Stacking them in one flex column keeps the gaps between items equal. -->
  <div :class="['legend-container', { 'sidepanel-visible': isSidePanelVisible }]">
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
  bottom: var(--map-cadastre-bottom);
}

.cadastre-info-container > * {
  @apply pointer-events-auto;
}

@media (min-width: 1024px) {
  .cadastre-info-container.sidepanel-visible {
    left: calc(50% + var(--width-sidepanel) / 2);
  }
}

.bottom-left-controls {
  @apply absolute flex flex-col items-start gap-2;
  @apply transition-all duration-300 ease-out;
  z-index: var(--z-map-overlay);
  left: var(--map-edge-gap);
  bottom: var(--map-overlay-bottom);
}

@media (min-width: 1024px) {
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
