<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { SelectionMode } from "@/utils/enum"
import Button from "primevue/button"

const mapStore = useMapStore()

const drawingInfo = computed(() => {
  const mode = mapStore.selectionMode
  const baseTitle = "Sélection"
  const modeLabels: Partial<Record<SelectionMode, string>> = {
    [SelectionMode.POINT]: "Clic simple",
    [SelectionMode.POLYGON]: `${baseTitle} polygone`,
    [SelectionMode.RECTANGLE]: `${baseTitle} rectangle`,
    [SelectionMode.CIRCLE]: `${baseTitle} cercle`,
    [SelectionMode.ANGLED_RECTANGLE]: `${baseTitle} rectangle incliné`,
    [SelectionMode.SECTOR]: `${baseTitle} secteur`
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
    v-if="mapStore.isShapeMode"
    class="absolute top-2 left-1/2 -translate-x-1/2 z-50 max-w-md"
    data-cy="drawing-controls"
    @click.stop
  >
    <div class="bg-white rounded-lg p-4 flex flex-col">
      <div class="text-center text-brown font-semibold">{{ drawingInfo }}</div>

      <div class="text-center text-sm text-gray-600 mb-2">
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
          data-cy="drawing-cancel"
          outlined
          severity="secondary"
          size="small"
          @click="cancelDrawing"
        >
          <i class="pi pi-times mr-2"></i>
          Annuler
        </Button>
      </div>
    </div>
  </div>
</template>
