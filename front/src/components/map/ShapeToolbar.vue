<script lang="ts" setup>
import { computed, ref } from "vue"
import { useMapStore } from "@/stores/map"
import { useAppStore } from "@/stores/app"
import { SelectionMode } from "@/utils/enum"
import IconClose from "@/components/icons/IconClose.vue"

const mapStore = useMapStore()
const appStore = useAppStore()

// Keep the centered panel centered within the visible map area when the side
// panel pushes content aside (desktop only — mirrors the other centered overlays).
const isSidePanelVisible = computed(() => appStore.sidePanelVisible)

// Local disclosure state: the centered card is hidden behind a single trigger.
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

// Header doubles as feedback: generic while idle, the active shape's name otherwise.
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
  <!-- Single round trigger, anchored where the legacy draw toggle lived. -->
  <button
    v-tooltip.left="'Dessiner une zone'"
    class="shape-toolbar__trigger map-control-btn map-control-btn-sm"
    :class="{ 'map-control-btn-active': isTriggerActive }"
    type="button"
    data-cy="shape-toolbar-toggle"
    :aria-expanded="isOpen"
    aria-controls="shape-toolbar-panel"
    aria-label="Dessiner une zone"
    @click="toggleOpen"
  >
    <img :src="triggerIcon" alt="" aria-hidden="true" class="w-6 h-6" />
  </button>

  <!-- Open card is centered, independent of the trigger position. -->
  <div
    v-if="isOpen"
    id="shape-toolbar-panel"
    class="shape-toolbar"
    :class="{ 'sidepanel-visible': isSidePanelVisible }"
    data-cy="shape-toolbar"
    role="toolbar"
    aria-label="Outils de forme"
  >
    <span class="shape-toolbar__title">{{ panelTitle }}</span>

    <ShapeModePicker class="shape-toolbar__picker" />

    <template v-if="state !== 'point'">
      <span class="shape-toolbar__rule" aria-hidden="true" />
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
            class="shape-toolbar__clear"
            type="button"
            data-cy="shape-clear"
            aria-label="Effacer la sélection"
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

/* Centered card: flat language (rounded-lg, no shadow) to match the map panels;
   fixed width so the variable hint text never resizes it. It is centered in the
   band between the bottom-left controls' right edge (their live width is
   published by MapComponent) and the draw trigger's left edge, re-centering
   automatically when either side resizes or the side panel toggles. */
.shape-toolbar {
  @apply absolute
         flex flex-col items-stretch gap-2 p-3
         bg-white border border-gray-200 rounded-lg
         w-64 max-w-[calc(100vw-1rem)]
         transition-all duration-300 ease-out;
  z-index: var(--z-map-overlay);
  bottom: var(--map-panel-bottom);
  --shape-band-left: calc(
    var(--map-edge-gap) + var(--bottom-left-controls-width, 0px) + var(--map-edge-gap)
  );
  --shape-band-right: calc(
    100% - var(--map-trigger-right) - var(--map-trigger-size) - var(--map-edge-gap)
  );
  left: calc((var(--shape-band-left) + var(--shape-band-right)) / 2);
  transform: translateX(-50%);
}
@media (min-width: 1024px) {
  .shape-toolbar.sidepanel-visible {
    --shape-band-left: calc(
      var(--width-sidepanel) + var(--map-edge-gap) + var(--bottom-left-controls-width, 0px) +
        var(--map-edge-gap)
    );
  }
}
.shape-toolbar__title {
  @apply text-[11px] font-bold uppercase tracking-wider text-gray-400;
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
