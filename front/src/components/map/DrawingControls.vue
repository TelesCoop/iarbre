<script lang="ts" setup>
import { computed, ref } from "vue"
import { useMapStore } from "@/stores/map"
import { SelectionMode } from "@/utils/enum"
import Button from "primevue/button"

const mapStore = useMapStore()
const isCalculating = ref(false)

const isShapeMode = computed(() => mapStore.selectionMode !== SelectionMode.POINT)
const canFinish = computed(() => {
  const features = mapStore.shapeDrawing.getSelectedFeatures()
  return features && features.length > 0
})
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

const finishDrawing = async () => {
  if (isCalculating.value) return

  isCalculating.value = true
  try {
    await mapStore.finishShapeSelection()
  } finally {
    isCalculating.value = false
  }
}

const cancelDrawing = () => {
  mapStore.shapeDrawing.clearDrawing()
  mapStore.changeSelectionMode(SelectionMode.POINT)
}
</script>

<template>
  <div
    v-if="isShapeMode"
    class="absolute top-4 left-1/2 transform -translate-x-1/2 z-50"
    data-cy="drawing-controls"
    @click.stop
  >
    <div class="bg-white rounded-lg shadow-lg p-4 flex flex-col gap-3">
      <div class="text-center text-brown font-semibold">{{ drawingInfo }}</div>

      <div class="text-center text-sm text-gray-600">
        <template v-if="mapStore.selectionMode === SelectionMode.POLYGON">
          Cliquez sur la carte pour dessiner un polygone
        </template>
        <template v-else-if="mapStore.selectionMode === SelectionMode.RECTANGLE">
          Cliquez et glissez pour dessiner un rectangle
        </template>
        <template v-else-if="mapStore.selectionMode === SelectionMode.CIRCLE">
          Cliquez et glissez pour dessiner un cercle
        </template>
        <template v-else> Dessinez votre forme sur la carte </template>
      </div>

      <div class="flex gap-2">
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

        <Button
          label="Calculer"
          icon="pi pi-check"
          severity="success"
          size="small"
          :disabled="!canFinish"
          :loading="isCalculating"
          data-cy="drawing-finish"
          @click="finishDrawing"
        />
      </div>
    </div>
  </div>
</template>
