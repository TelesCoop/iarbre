<script lang="ts" setup>
import { computed, ref } from "vue"
import { useMapStore } from "@/stores/map"
import { SelectionMode } from "@/utils/enum"
import IconClose from "@/components/icons/IconClose.vue"

const mapStore = useMapStore()

// Local disclosure state: the card is hidden behind a single trigger.
// Closing only hides the card — the drawn shape and its score are kept; use the
// clear (✕) action inside the card to actually discard the selection.
const isOpen = ref(false)
const toggleOpen = () => {
  isOpen.value = !isOpen.value
}

const state = computed(() => mapStore.drawingState)
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

  <!-- Card opens in the top-right corner, just below the search bar. -->
  <div
    v-if="isOpen"
    id="shape-toolbar-panel"
    aria-label="Outils de forme"
    class="shape-toolbar__panel"
    data-cy="shape-toolbar"
    role="toolbar"
  >
    <span class="shape-toolbar__title">{{ panelTitle }}</span>

    <ShapeModePicker class="shape-toolbar__picker" />

    <template v-if="state !== 'point'">
      <span aria-hidden="true" class="shape-toolbar__rule" />
      <div class="shape-toolbar__actions">
        <p class="shape-toolbar__hint">{{ contextHint }}</p>
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

/* Disclosure card, anchored top-right just below the search bar and matching its
   width (both right-aligned at --map-edge-gap, so edges line up). MapComponent
   publishes the bar's live height and width. Flat language (rounded-lg, no
   shadow) to match the map panels. */
.shape-toolbar__panel {
  @apply absolute flex flex-col items-stretch gap-2 p-3
         bg-white border border-gray-200 rounded-lg
         max-w-[calc(100vw-1rem)]
         transition-all duration-300 ease-out;
  z-index: var(--z-map-overlay);
  top: calc(var(--map-edge-gap) + var(--top-right-controls-height, 0px) + var(--map-edge-gap));
  right: var(--map-edge-gap);
  /* Never shrink below the mode picker: the search bar is only half-width on
     mobile, narrower than the five shape buttons. */
  width: var(--top-right-controls-width, 15rem);
  min-width: min-content;
}
.shape-toolbar__title {
  @apply text-[11px] font-bold uppercase tracking-wider text-gray-600;
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
