<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { SelectionMode } from "@/utils/enum"
import Button from "primevue/button"

const mapStore = useMapStore()

interface DrawingMode {
  mode: SelectionMode
  icon: string
  label: string
  dataCy: string
}

const drawingModes: DrawingMode[] = [
  {
    mode: SelectionMode.POINT,
    icon: "point",
    label: "Sélection par point",
    dataCy: "selection-mode-point"
  },
  {
    mode: SelectionMode.POLYGON,
    icon: "polygon",
    label: "Sélection par polygone",
    dataCy: "selection-mode-polygon"
  },
  {
    mode: SelectionMode.RECTANGLE,
    icon: "rectangle",
    label: "Sélection par rectangle",
    dataCy: "selection-mode-rectangle"
  },
  {
    mode: SelectionMode.CIRCLE,
    icon: "circle",
    label: "Sélection par cercle",
    dataCy: "selection-mode-circle"
  },
  {
    mode: SelectionMode.ANGLED_RECTANGLE,
    icon: "angled-rectangle",
    label: "Sélection par rectangle incliné",
    dataCy: "selection-mode-angled-rectangle"
  },
  {
    mode: SelectionMode.SECTOR,
    icon: "sector",
    label: "Sélection par secteur",
    dataCy: "selection-mode-sector"
  }
]

const isActive = (mode: SelectionMode) => computed(() => mapStore.selectionMode === mode)

const switchMode = (mode: SelectionMode) => {
  mapStore.changeSelectionMode(mode)
}
</script>

<template>
  <div class="flex flex-col gap-0 overflow-hidden rounded-lg">
    <Button
      v-for="drawingMode in drawingModes"
      :key="drawingMode.mode"
      v-tooltip.left="drawingMode.label"
      :class="[
        'w-10 h-10 p-0 flex items-center justify-center border rounded-none! border-gray-200! selection-mode-btn',
        isActive(drawingMode.mode).value ? 'bg-primary active' : 'bg-white!'
      ]"
      :data-cy="drawingMode.dataCy"
      severity=""
      size="small"
      @click="switchMode(drawingMode.mode)"
    >
      <img
        :alt="drawingMode.label"
        :src="`/icons/${drawingMode.icon}${isActive(drawingMode.mode).value ? '-white' : ''}.svg`"
        class="w-6 h-6 selection-mode-icon"
      />
    </Button>
  </div>
</template>

<style scoped></style>
