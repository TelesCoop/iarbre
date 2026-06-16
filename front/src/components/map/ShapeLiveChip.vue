<script lang="ts" setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue"
import { useRouter } from "vue-router"
import { useMapStore } from "@/stores/map"
import { useZoneStore } from "@/stores/zone"
import { formatArea, computePolygonAreaM2 } from "@/utils/geo"

const mapStore = useMapStore()
const zoneStore = useZoneStore()
const router = useRouter()

const screenPos = ref<{ x: number; y: number } | null>(null)
// Cached so the high-frequency map "render" handler only reprojects a known point
// instead of re-reading the whole TerraDraw snapshot on every frame.
const centroidLngLat = ref<[number, number] | null>(null)
const areaM2 = ref<number | null>(null)

const mapInstance = computed(() => mapStore.mapInstancesByIds["default"] ?? null)

const isClosedRing = (coords: number[][]): boolean =>
  coords.length > 1 &&
  coords[0][0] === coords[coords.length - 1][0] &&
  coords[0][1] === coords[coords.length - 1][1]

const centroid = (coords: number[][]): [number, number] => {
  // Drop the repeated closing vertex so it doesn't bias the average toward the first point.
  const points = isClosedRing(coords) ? coords.slice(0, -1) : coords
  const sum = points.reduce((acc, [lng, lat]) => [acc[0] + lng, acc[1] + lat], [0, 0])
  return [sum[0] / points.length, sum[1] / points.length]
}

const reproject = () => {
  const map = mapInstance.value
  if (!map || !centroidLngLat.value) {
    screenPos.value = null
    return
  }
  screenPos.value = map.project(centroidLngLat.value)
}

// Reads the TerraDraw snapshot — call only on shape/area change, never per render frame.
const refreshFromShape = () => {
  const coords = mapStore.shapeDrawing.getCurrentShapeCoordinates()
  if (!coords || coords.length < 3 || mapStore.drawingState === "point") {
    centroidLngLat.value = null
    areaM2.value = null
    screenPos.value = null
    return
  }
  centroidLngLat.value = centroid(coords)
  // liveArea is normally set by the store; the fallback covers the brief window
  // before the first change/finish event populates it.
  areaM2.value = mapStore.liveArea ?? computePolygonAreaM2(coords)
  reproject()
}

const areaLabel = computed(() => (areaM2.value === null ? null : formatArea(areaM2.value)))

const isAreaTooLarge = computed(() => mapStore.isAreaTooLarge)
const isCalculating = computed(() => mapStore.isCalculating)

const isVisible = computed(() => screenPos.value !== null && areaLabel.value !== null)

// Only once the zone is finalized and its scores are available.
const showDashboardButton = computed(() => mapStore.hasShapeContextData)

const goToZoneDashboard = () => {
  const polygon = mapStore.getDrawnPolygon()
  if (!polygon) return
  zoneStore.setZone(polygon)
  // Capture the geometry first, then tear down the drawing session so the chip
  // and shape state don't linger once we leave the map.
  mapStore.exitShapeMode()
  router.push({ name: "dashboard" })
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
</script>

<template>
  <div
    v-if="isVisible"
    class="shape-live-chip"
    :class="{ 'shape-live-chip--warning': isAreaTooLarge }"
    data-cy="shape-live-chip"
    :style="{ left: `${screenPos!.x}px`, top: `${screenPos!.y}px` }"
  >
    <div class="shape-live-chip__pill" aria-hidden="true">
      <span class="shape-live-chip__dot" />
      <span>{{ areaLabel }}</span>
      <span v-if="isAreaTooLarge"> · Zone trop grande</span>
      <span
        v-else-if="isCalculating"
        class="shape-live-chip__spinner"
        data-cy="shape-live-chip-spinner"
      />
    </div>
    <button
      v-if="showDashboardButton"
      type="button"
      class="shape-live-chip__cta"
      data-cy="zone-dashboard-cta"
      @click="goToZoneDashboard"
    >
      Voir le tableau de bord
    </button>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.shape-live-chip {
  @apply absolute -translate-x-1/2 -translate-y-1/2 pointer-events-none
         flex flex-col items-center gap-1.5;
  z-index: var(--z-map-overlay);
}
.shape-live-chip__pill {
  @apply flex items-center gap-2 px-2.5 py-1.5 rounded-full
         text-xs font-semibold text-white bg-gray-900 whitespace-nowrap;
}
.shape-live-chip--warning .shape-live-chip__pill {
  @apply bg-red-700;
}
.shape-live-chip__cta {
  @apply pointer-events-auto cursor-pointer
         px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap
         text-white bg-primary-600 shadow-md transition-colors
         hover:bg-primary-700 focus-visible:outline-2 focus-visible:outline-offset-2
         focus-visible:outline-primary-600;
}
.shape-live-chip__dot {
  @apply w-2 h-2 rounded-full bg-primary-300;
}
.shape-live-chip--warning .shape-live-chip__dot {
  @apply bg-white;
}
.shape-live-chip__spinner {
  @apply w-3 h-3 rounded-full;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: #ffffff;
  animation: shape-live-chip-spin 0.7s linear infinite;
}
@keyframes shape-live-chip-spin {
  to {
    transform: rotate(360deg);
  }
}
@media (prefers-reduced-motion: reduce) {
  .shape-live-chip__spinner {
    animation: none;
  }
}
</style>
