<script lang="ts" setup>
import { computed, ref, watch } from "vue"
import { useRouter } from "vue-router"
import { useEventListener } from "@vueuse/core"
import { useTapOutside } from "@/composables/useTapOutside"
import { useMapStore } from "@/stores/map"
import { useZoneStore } from "@/stores/zone"
import { SelectionMode } from "@/utils/enum"
import { formatArea } from "@/utils/geo"
import IconClose from "@/components/icons/IconClose.vue"

const mapStore = useMapStore()
const zoneStore = useZoneStore()
const router = useRouter()

// Local disclosure state: the card is hidden behind a single trigger.
// Closing only hides the card — the drawn shape and its score are kept; use the
// clear (✕) action inside the card to actually discard the selection.
const isOpen = ref(false)
const toggleOpen = () => {
  isOpen.value = !isOpen.value
}

const state = computed(() => mapStore.drawingState)

// A finished shape is when the zone can be analysed, so its actions come into view.
watch(state, (newState) => {
  if (newState === "editing") isOpen.value = true
})

const areaLabel = computed(() =>
  mapStore.liveArea !== null ? formatArea(mapStore.liveArea) : null
)

const analyzeZone = () => {
  const polygon = mapStore.getDrawnPolygon()
  if (!polygon) return
  zoneStore.setZone(polygon)
  mapStore.exitShapeMode()
  router.push({ name: "dashboard" })
}

const triggerRef = ref<HTMLElement | null>(null)
const panelRef = ref<HTMLElement | null>(null)

// While a shape is drawn or edited, taps on the map are drawing gestures, not a dismissal.
const isDrawingOnMap = (event: PointerEvent) =>
  state.value !== "point" && (event.target as Element).closest(".maplibregl-map") !== null

useTapOutside(
  panelRef,
  (event) => {
    if (!isDrawingOnMap(event)) isOpen.value = false
  },
  { ignore: [triggerRef] }
)
// Scoped to the toolbar: Escape elsewhere cancels a drawing or closes a dialog.
const closeOnEscape = (event: KeyboardEvent) => {
  if (event.key === "Escape") isOpen.value = false
}
useEventListener(triggerRef, "keydown", closeOnEscape)
useEventListener(panelRef, "keydown", closeOnEscape)

const isPolygon = computed(() => mapStore.selectionMode === SelectionMode.POLYGON)

// Highlight the trigger whenever the panel is open or a shape is currently active,
// so a collapsed-but-active selection stays discoverable.
const isTriggerActive = computed(() => isOpen.value || state.value !== "point")

// Idle shows the generic tool glyph; once a shape is active the trigger mirrors it,
// so the current selection mode is readable even when the card is collapsed.
const triggerIcon = computed(() => {
  const suffix = isTriggerActive.value ? "-white" : ""
  const name = state.value === "point" ? "shape-tool" : mapStore.selectionMode
  return `/icons/${name}${suffix}.svg`
})

const SHAPE_LABELS: Record<SelectionMode, string> = {
  [SelectionMode.POINT]: "Point",
  [SelectionMode.POLYGON]: "Polygone",
  [SelectionMode.RECTANGLE]: "Rectangle",
  [SelectionMode.CIRCLE]: "Cercle",
  [SelectionMode.ANGLED_RECTANGLE]: "Rectangle incliné",
  [SelectionMode.SELECT]: "Sélection"
}

const panelTitle = computed(() =>
  state.value === "point" ? "Forme" : (SHAPE_LABELS[mapStore.selectionMode] ?? "Forme")
)

const contextHint = computed(() => {
  if (state.value === "editing") {
    // A circle is moved as a whole; other shapes have draggable vertices.
    return mapStore.selectionMode === SelectionMode.CIRCLE
      ? "Glissez la forme pour la déplacer"
      : "Glissez les sommets pour ajuster"
  }
  return isPolygon.value
    ? "Cliquez les sommets, Entrée pour terminer"
    : "Cliquez-glissez pour dessiner"
})

const handleFinish = () => mapStore.shapeDrawing.finishCurrentPolygon()
const handleNewShape = () => mapStore.startNewShape(mapStore.selectionMode)
const handleClear = () => mapStore.exitShapeMode()
</script>

<template>
  <button
    ref="triggerRef"
    v-tooltip.left="'Dessiner une zone'"
    :aria-expanded="isOpen"
    :class="{ 'map-control-btn-active': isTriggerActive }"
    aria-controls="shape-toolbar-panel"
    aria-label="Dessiner une zone"
    class="shape-toolbar__trigger map-control-btn map-control-btn-sm"
    data-cy="shape-toolbar-toggle"
    type="button"
    @click="toggleOpen"
  >
    <img :src="triggerIcon" alt="" aria-hidden="true" class="w-6 h-6" />
  </button>

  <div
    v-if="isOpen"
    id="shape-toolbar-panel"
    ref="panelRef"
    aria-label="Outils de forme"
    class="map-control-panel shape-toolbar__panel"
    data-cy="shape-toolbar"
    role="toolbar"
  >
    <div class="shape-toolbar__header">
      <span class="map-panel-title">{{ panelTitle }}</span>
      <span v-if="state === 'editing' && areaLabel" class="shape-toolbar__area">
        {{ areaLabel }}
      </span>
    </div>

    <ShapeModePicker class="shape-toolbar__picker" />

    <template v-if="state !== 'point'">
      <span aria-hidden="true" class="shape-toolbar__rule" />
      <div class="shape-toolbar__actions">
        <p class="shape-toolbar__hint">{{ contextHint }}</p>
        <AppButton
          v-if="state === 'editing'"
          data-cy="zone-dashboard-cta"
          full-width
          size="sm"
          variant="primary"
          @click="analyzeZone"
        >
          Afficher le tableau de bord de la zone
        </AppButton>
        <div class="shape-toolbar__buttons">
          <AppButton
            v-if="state === 'drawing' && isPolygon"
            class="h-11"
            data-cy="shape-finish"
            size="sm"
            variant="primary"
            @click="handleFinish"
          >
            Terminer
          </AppButton>
          <AppButton
            v-else-if="state === 'editing'"
            class="h-11"
            data-cy="shape-new"
            size="sm"
            variant="secondary"
            @click="handleNewShape"
          >
            Nouvelle forme
          </AppButton>
          <button
            v-tooltip="'Effacer la sélection'"
            aria-label="Effacer la sélection"
            class="shape-toolbar__clear"
            data-cy="shape-clear"
            type="button"
            @click="handleClear"
          >
            <IconClose :size="16" aria-hidden="true" />
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

/* Trigger reuses the shared map-control button styling and the centralized map
   layout tokens, so it stays flush with the maplibre controls' visual bottom. */
.shape-toolbar__trigger {
  @apply absolute;
  z-index: var(--z-map-overlay);
  bottom: var(--map-overlay-bottom);
  right: var(--map-trigger-right);
}

/* Disclosure card. On phones the search column is narrower than the mode picker,
   so the card opens above its trigger instead of over the legend. */
.shape-toolbar__panel {
  @apply absolute flex flex-col items-stretch gap-2
         transition-all duration-300 ease-out;
  z-index: var(--z-map-raised);
  bottom: var(--map-above-bottom-row);
  right: var(--map-trigger-right);
  min-width: min-content;
}

/* Below the search bar and matching its width, right-aligned on the same edge. */
@media (min-width: 768px) {
  .shape-toolbar__panel {
    top: calc(var(--map-edge-gap) + var(--top-right-controls-height, 0px) + var(--map-edge-gap));
    right: var(--map-edge-gap);
    bottom: auto;
    width: var(--top-right-controls-width, 15rem);
  }
}
.shape-toolbar__header {
  @apply flex items-baseline justify-between gap-3;
}
.shape-toolbar__area {
  @apply text-sm font-semibold text-gray-900 whitespace-nowrap;
}
.shape-toolbar__picker {
  @apply justify-center;
}
.shape-toolbar__rule {
  @apply h-px w-full bg-gray-200;
}
.shape-toolbar__actions {
  @apply flex flex-col items-center gap-2;
}
.shape-toolbar__buttons {
  @apply flex items-center justify-center gap-2;
}
.shape-toolbar__hint {
  @apply text-xs text-center text-gray-500;
}
/* 44px square keeps the discard action above the minimum touch target. */
.shape-toolbar__clear {
  @apply flex items-center justify-center w-11 h-11 rounded-lg shrink-0
         text-gray-500 transition-colors duration-200
         hover:bg-red-50 hover:text-red-600;
}
</style>
