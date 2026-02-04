<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { SelectionMode } from "@/utils/enum"
import IconClose from "@/components/icons/IconClose.vue"

const mapStore = useMapStore()

const SELECTION_MODE_LABELS: Record<SelectionMode, string> = {
  [SelectionMode.POINT]: "Clic simple",
  [SelectionMode.POLYGON]: "Sélection polygone",
  [SelectionMode.RECTANGLE]: "Sélection rectangle",
  [SelectionMode.CIRCLE]: "Sélection cercle",
  [SelectionMode.ANGLED_RECTANGLE]: "Sélection rectangle incliné",
  [SelectionMode.SECTOR]: "Sélection secteur",
  [SelectionMode.SELECT]: "Sélection"
}

const isVisible = computed(() => mapStore.isShapeMode)
const currentMode = computed(() => mapStore.selectionMode)

const title = computed(() => SELECTION_MODE_LABELS[currentMode.value] ?? "")

const instructions: Record<SelectionMode, string> = {
  [SelectionMode.POLYGON]: "polygon",
  [SelectionMode.RECTANGLE]: "drag",
  [SelectionMode.CIRCLE]: "drag",
  [SelectionMode.ANGLED_RECTANGLE]: "drag",
  [SelectionMode.SECTOR]: "drag",
  [SelectionMode.POINT]: "default",
  [SelectionMode.SELECT]: "default"
}

const instructionType = computed(() => instructions[currentMode.value] || "default")

const handleCancel = () => {
  mapStore.shapeDrawing.clearDrawing()
  mapStore.changeSelectionMode(SelectionMode.POINT)
}
</script>

<template>
  <div
    v-if="isVisible"
    class="drawing-controls-wrapper"
    data-cy="drawing-controls"
    role="dialog"
    aria-labelledby="drawing-controls-title"
    @click.stop
  >
    <div class="drawing-controls-panel">
      <h2 id="drawing-controls-title" class="panel-title">
        {{ title }}
      </h2>

      <p class="panel-instructions">
        <template v-if="instructionType === 'polygon'">
          Dessinez un polygone. Appuyez sur <strong>Entrée ⏎</strong> pour terminer (3 points
          minimum).
        </template>
        <template v-else-if="instructionType === 'drag'">
          Cliquez et glissez pour dessiner.
        </template>
        <template v-else> Dessinez votre forme sur la carte. </template>
      </p>

      <div class="panel-actions">
        <AppButton data-cy="drawing-cancel" size="sm" variant="secondary" @click="handleCancel">
          <template #icon-left>
            <IconClose :size="16" aria-hidden="true" />
          </template>
          Annuler
        </AppButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.drawing-controls-wrapper {
  @apply absolute bottom-20 lg:bottom-14 left-1/2 -translate-x-1/2 z-50;
}

.drawing-controls-panel {
  @apply flex flex-col gap-2 py-3 px-4 bg-white border border-gray-200 rounded-lg whitespace-nowrap;
}

.panel-title {
  @apply text-center text-brown font-semibold;
}

.panel-instructions {
  @apply text-center text-sm text-gray-600 mb-2;
}

.panel-actions {
  @apply flex justify-center;
}
</style>
