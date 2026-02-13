<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { SelectionMode } from "@/utils/enum"

interface SelectionModeOption {
  mode: SelectionMode
  icon: string
  label: string
  dataCy: string
}

const mapStore = useMapStore()

const selectionModes: SelectionModeOption[] = [
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

const currentMode = computed(() => mapStore.selectionMode)

const isActive = (mode: SelectionMode): boolean => currentMode.value === mode

const handleModeChange = (mode: SelectionMode) => {
  mapStore.changeSelectionMode(mode)
}
</script>

<template>
  <div class="map-control-group" role="toolbar" aria-label="Modes de sélection">
    <SelectionModeButton
      v-for="option in selectionModes"
      :key="option.mode"
      :active="isActive(option.mode)"
      :data-cy="option.dataCy"
      :icon="option.icon"
      :label="option.label"
      :mode="option.mode"
      @select="handleModeChange"
    />
  </div>
</template>
