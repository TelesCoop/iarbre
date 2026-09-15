<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { SelectionMode, DataType } from "@/utils/enum"

interface ShapeOption {
  mode: SelectionMode
  icon: string
  label: string
  dataCy: string
}

const mapStore = useMapStore()

const shapeOptions: ShapeOption[] = [
  {
    mode: SelectionMode.POINT,
    icon: "point",
    label: "Sélection par point",
    dataCy: "shape-mode-point"
  },
  {
    mode: SelectionMode.POLYGON,
    icon: "polygon",
    label: "Sélection par polygone",
    dataCy: "shape-mode-polygon"
  },
  {
    mode: SelectionMode.RECTANGLE,
    icon: "rectangle",
    label: "Sélection par rectangle",
    dataCy: "shape-mode-rectangle"
  },
  {
    mode: SelectionMode.CIRCLE,
    icon: "circle",
    label: "Sélection par cercle",
    dataCy: "shape-mode-circle"
  },
  {
    mode: SelectionMode.ANGLED_RECTANGLE,
    icon: "angled-rectangle",
    label: "Sélection par rectangle incliné",
    dataCy: "shape-mode-angled-rectangle"
  }
]

const isClimateZone = computed(() => mapStore.selectedDataType === DataType.CLIMATE_ZONE)

const isDisabled = (mode: SelectionMode): boolean =>
  isClimateZone.value && mode !== SelectionMode.POINT

const isActive = (mode: SelectionMode): boolean => mapStore.selectionMode === mode

const handleSelect = (mode: SelectionMode) => {
  if (isDisabled(mode)) return
  if (mode === SelectionMode.POINT) {
    mapStore.exitShapeMode()
    return
  }
  if (mapStore.drawingState === "editing") {
    mapStore.startNewShape(mode)
  } else {
    mapStore.enterShapeMode(mode)
  }
}
</script>

<template>
  <div class="shape-mode-picker" role="group" aria-label="Formes de sélection">
    <SelectionModeButton
      v-for="option in shapeOptions"
      :key="option.mode"
      :active="isActive(option.mode)"
      :disabled="isDisabled(option.mode)"
      :data-cy="option.dataCy"
      :icon="option.icon"
      :label="option.label"
      :mode="option.mode"
      @select="handleSelect"
    />
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.shape-mode-picker {
  @apply flex items-center gap-1;
}
</style>
