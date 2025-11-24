<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { SelectionMode } from "@/utils/enum"
import Button from "primevue/button"

const mapStore = useMapStore()

const isShapeMode = computed(() => mapStore.selectionMode !== SelectionMode.POINT)
const drawingInfo = computed(() => {
  const mode = mapStore.selectionMode
  const modeLabels: Partial<Record<SelectionMode, string>> = {
    [SelectionMode.POINT]: "Clic simple",
    [SelectionMode.POLYGON]: "Dessin de polygone",
    [SelectionMode.RECTANGLE]: "Dessin de rectangle",
    [SelectionMode.CIRCLE]: "Dessin de cercle",
    [SelectionMode.ANGLED_RECTANGLE]: "Dessin de rectangle incliné",
    [SelectionMode.SECTOR]: "Dessin de secteur"
  }
  return modeLabels[mode] || ""
})

const cancelDrawing = () => {
  mapStore.shapeDrawing.clearDrawing()
  mapStore.changeSelectionMode(SelectionMode.POINT)
}
</script>

<template>
  <div
    v-if="isShapeMode"
    class="absolute bottom-4 left-1/2 z-50 max-w-md"
    data-cy="drawing-controls"
    @click.stop
  >
    <div class="bg-white rounded-lg shadow-lg p-4 flex flex-col gap-3">
      <div class="text-center text-brown font-semibold">{{ drawingInfo }}</div>

      <div class="text-center text-sm text-gray-600">
        <template v-if="mapStore.selectionMode === SelectionMode.POLYGON">
          Dessinez un polygone. Appuyez sur <strong>Entrée ⏎</strong> pour terminer (3 points
          minimum).
        </template>
        <template v-else-if="mapStore.selectionMode === SelectionMode.RECTANGLE">
          Cliquez et glissez pour dessiner.
        </template>
        <template v-else-if="mapStore.selectionMode === SelectionMode.CIRCLE">
          Cliquez et glissez pour dessiner.
        </template>
        <template v-else> Dessinez votre forme sur la carte. </template>
      </div>

      <div class="flex justify-center">
        <Button
          severity="secondary"
          outlined
          size="small"
          data-cy="drawing-cancel"
          @click="cancelDrawing"
        >
          <i class="pi pi-times mr-2"></i>
          Annuler
        </Button>
      </div>
    </div>
  </div>
</template>
