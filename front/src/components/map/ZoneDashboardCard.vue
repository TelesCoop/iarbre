<script lang="ts" setup>
import { computed } from "vue"
import { useRouter } from "vue-router"
import { useMapStore } from "@/stores/map"
import { useZoneStore } from "@/stores/zone"
import { useAppStore } from "@/stores/app"
import { formatArea } from "@/utils/geo"
import AppButton from "@/components/shared/AppButton.vue"

const mapStore = useMapStore()
const zoneStore = useZoneStore()
const appStore = useAppStore()
const router = useRouter()

// Shown once the selection is finished (the shape is being edited, not drawn).
const isVisible = computed(() => mapStore.drawingState === "editing")
const areaLabel = computed(() =>
  mapStore.liveArea !== null ? formatArea(mapStore.liveArea) : null
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
    :class="['zone-dashboard-card', { 'sidepanel-visible': appStore.sidePanelVisible }]"
    data-cy="zone-dashboard-card"
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
         bg-white border border-gray-200 rounded-lg shadow-md;
  @apply transition-all duration-300 ease-out;
  z-index: var(--z-map-overlay);
  left: 50%;
  transform: translateX(-50%);
  bottom: var(--map-overlay-bottom);
  min-width: 12rem;
}

.zone-dashboard-card__info {
  @apply flex items-baseline justify-between gap-3;
}

.zone-dashboard-card__label {
  @apply text-[11px] font-bold uppercase tracking-wider text-gray-500;
}

.zone-dashboard-card__area {
  @apply text-sm font-semibold text-gray-900 whitespace-nowrap;
}

@media (min-width: 1024px) {
  .zone-dashboard-card.sidepanel-visible {
    left: calc(50% + var(--width-sidepanel) / 2);
  }
}
</style>
