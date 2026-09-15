<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { useAppStore } from "@/stores/app"
import { onMounted, onBeforeUnmount, ref, computed, type PropType } from "vue"
import { type MapParams } from "@/types/map"
import ZoneDashboardCard from "@/components/map/ZoneDashboardCard.vue"

const props = defineProps({
  mapId: {
    required: true,
    type: String
  },
  initialFilters: {
    required: false,
    type: Array as PropType<(number | string)[]>,
    default: () => []
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

// Mirror the search bar's height and width onto CSS vars so the shape toolbar's
// card can sit just below it and match its width — without hard-coding either.
const topRightControlsEl = ref<HTMLElement | null>(null)
const setTopRightSize = (el: HTMLElement | null) => {
  const root = document.documentElement.style
  root.setProperty("--top-right-controls-height", `${el?.offsetHeight ?? 0}px`)
  root.setProperty("--top-right-controls-width", `${el?.offsetWidth ?? 0}px`)
}
let topRightObserver: ResizeObserver | null = null

onMounted(() => {
  mapStore.initMap(props.mapId, model.value.dataType!, props.initialFilters)
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

  if (topRightControlsEl.value) {
    topRightObserver = new ResizeObserver(() => setTopRightSize(topRightControlsEl.value))
    topRightObserver.observe(topRightControlsEl.value)
    setTopRightSize(topRightControlsEl.value)
  }
})

onBeforeUnmount(() => {
  topRightObserver?.disconnect()
  setTopRightSize(null)
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
    <MapCopyLinkButton />
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
