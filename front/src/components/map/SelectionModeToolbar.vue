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
    label: "Point",
    dataCy: "selection-mode-point"
  },
  {
    mode: SelectionMode.POLYGON,
    icon: "polygon",
    label: "Polygone",
    dataCy: "selection-mode-polygon"
  },
  {
    mode: SelectionMode.RECTANGLE,
    icon: "rectangle",
    label: "Rectangle",
    dataCy: "selection-mode-rectangle"
  },
  {
    mode: SelectionMode.CIRCLE,
    icon: "circle",
    label: "Cercle",
    dataCy: "selection-mode-circle"
  },
  {
    mode: SelectionMode.ANGLED_RECTANGLE,
    icon: "angled-rectangle",
    label: "Rectangle incliné",
    dataCy: "selection-mode-angled-rectangle"
  },
  {
    mode: SelectionMode.SECTOR,
    icon: "sector",
    label: "Secteur",
    dataCy: "selection-mode-sector"
  }
]

const isActive = (mode: SelectionMode) => computed(() => mapStore.selectionMode === mode)

const switchMode = (mode: SelectionMode) => {
  mapStore.changeSelectionMode(mode)
}
</script>

<template>
  <div class="flex flex-col gap-0 bg-white rounded-lg shadow-md overflow-hidden">
    <Button
      v-for="drawingMode in drawingModes"
      :key="drawingMode.mode"
      :data-cy="drawingMode.dataCy"
      size="small"
      :severity="isActive(drawingMode.mode).value ? 'secondary' : ''"
      class="w-10 h-10 p-0 flex items-center justify-center rounded-none! border-0!"
      @click="switchMode(drawingMode.mode)"
    >
      <img
        :src="`/icons/${drawingMode.icon}${isActive(drawingMode.mode).value ? '-white' : ''}.svg`"
        :alt="drawingMode.label"
        class="w-6 h-6"
      />
    </Button>
  </div>
</template>
