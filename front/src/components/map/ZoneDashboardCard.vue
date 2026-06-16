<script lang="ts" setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue"
import { useRouter } from "vue-router"
import { useMapStore } from "@/stores/map"
import { useZoneStore } from "@/stores/zone"
import { formatArea } from "@/utils/geo"
import AppButton from "@/components/shared/AppButton.vue"

const mapStore = useMapStore()
const zoneStore = useZoneStore()
const router = useRouter()

// Cached ring (lng/lat) so the high-frequency "render" handler only reprojects a
// known shape instead of re-reading the TerraDraw snapshot on every frame.
const ringLngLat = ref<[number, number][] | null>(null)
const anchor = ref<{ x: number; y: number } | null>(null)

// Gap (px) between the shape's bounding box and the card.
const GAP = 12

// Shown once the selection is finished (the shape is being edited, not drawn).
const isFinished = computed(() => mapStore.drawingState === "editing")
const isVisible = computed(() => isFinished.value && anchor.value !== null)
const areaLabel = computed(() =>
  mapStore.liveArea !== null ? formatArea(mapStore.liveArea) : null
)

const mapInstance = computed(() => mapStore.mapInstancesByIds["default"] ?? null)

const reproject = () => {
  const map = mapInstance.value
  const ring = ringLngLat.value
  if (!map || !ring) {
    anchor.value = null
    return
  }
  const points = ring.map((coord) => map.project(coord))
  // Always anchor the card's top-left to the zone's top-right corner: a single,
  // stable side (no flipping) keeps it visually in the same place.
  const maxX = Math.max(...points.map((p) => p.x))
  const minY = Math.min(...points.map((p) => p.y))
  anchor.value = { x: maxX + GAP, y: minY }
}

const refreshFromShape = () => {
  if (!isFinished.value) {
    ringLngLat.value = null
    anchor.value = null
    return
  }
  ringLngLat.value = (mapStore.shapeDrawing.getCurrentShapeCoordinates() ?? null) as
    | [number, number][]
    | null
  reproject()
}

let attached = false
const attach = () => {
  const map = mapInstance.value
  if (!map || attached) return
  map.on("render", reproject)
  attached = true
  refreshFromShape()
}

onMounted(attach)
watch(mapInstance, attach)
watch(() => [mapStore.drawingState, mapStore.liveArea], refreshFromShape)

onBeforeUnmount(() => {
  const map = mapInstance.value
  if (map && attached) map.off("render", reproject)
  attached = false
})

const cardStyle = computed(() =>
  anchor.value ? { left: `${anchor.value.x}px`, top: `${anchor.value.y}px` } : {}
)

const analyzeZone = () => {
  const polygon = mapStore.getDrawnPolygon()
  if (!polygon) return
  zoneStore.setZone(polygon)
  // Capture the geometry first, then tear down the drawing session so the chip
  // and shape state don't linger once we leave the map.
  mapStore.exitShapeMode()
  router.push({ name: "dashboard" })
}
</script>

<template>
  <div
    v-if="isVisible"
    ref="cardEl"
    class="zone-dashboard-card"
    data-cy="zone-dashboard-card"
    :style="cardStyle"
  >
    <div class="zone-dashboard-card__info">
      <span class="zone-dashboard-card__label">Zone sélectionnée</span>
      <span v-if="areaLabel" class="zone-dashboard-card__area">{{ areaLabel }}</span>
    </div>
    <AppButton
      variant="primary"
      size="sm"
      full-width
      data-cy="zone-dashboard-cta"
      @click="analyzeZone"
    >
      Analyser cette zone
    </AppButton>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.zone-dashboard-card {
  @apply absolute flex flex-col gap-2 p-3
         bg-gray-200 border border-gray-300 rounded-lg;
  /* Interactive CTA tied to the selection: sits with the other floating controls,
     above the context-data side panel (--z-map-sheet) so it is never obscured. */
  z-index: var(--z-map-floating);
  /* Fixed size so the card never resizes as the area label changes. */
  width: 13rem;
}

.zone-dashboard-card__info {
  @apply flex items-baseline justify-between gap-3;
}

.zone-dashboard-card__label {
  @apply text-[11px] font-bold uppercase tracking-wider text-gray-600;
}

.zone-dashboard-card__area {
  @apply text-sm font-semibold text-gray-900 whitespace-nowrap;
}
</style>
