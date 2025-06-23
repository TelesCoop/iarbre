<script lang="ts" setup>
import { computed, ref } from "vue"
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"
import { LayerRenderMode } from "@/types/map"
import SelectButton from "primevue/selectbutton"

const mapStore = useMapStore()

const availableOptions = [
  {
    label: DataTypeToLabel[DataType.PLANTABILITY],
    value: DataType.PLANTABILITY
  },
  {
    label: DataTypeToLabel[DataType.VULNERABILITY],
    value: DataType.VULNERABILITY
  },
  {
    label: DataTypeToLabel[DataType.CLIMATE_ZONE],
    value: DataType.CLIMATE_ZONE
  }
]

const activeLayers = computed(() => mapStore.activeLayers)
const openPanels = ref<Set<DataType>>(new Set())

const isLayerActive = (dataType: DataType) => {
  return activeLayers.value.some((layer) => layer.dataType === dataType && layer.visible)
}

const togglePanel = (dataType: DataType) => {
  if (openPanels.value.has(dataType)) {
    openPanels.value.delete(dataType)
  } else {
    openPanels.value.add(dataType)
  }
}

const isPanelOpen = (dataType: DataType) => {
  return openPanels.value.has(dataType)
}

const deactivateLayer = (dataType: DataType) => {
  mapStore.removeLayer(dataType)

  // Mettre à jour selectedDataType vers le premier layer actif restant
  const remainingActiveLayer = activeLayers.value.find(
    (layer) => layer.visible && layer.dataType !== dataType
  )
  if (remainingActiveLayer) {
    mapStore.selectedDataType = remainingActiveLayer.dataType
  }
}

const activateLayerWithMode = (dataType: DataType, mode: LayerRenderMode | null) => {
  if (!mode) {
    deactivateLayer(dataType)
    return
  }

  mapStore.selectedDataType = dataType
  if (isLayerActive(dataType)) {
    const existingLayer = activeLayers.value.find(
      (layer) => layer.dataType === dataType && layer.visible
    )
    if (existingLayer && existingLayer.renderMode !== mode) {
      // Gestion dynamique des calques pleins lors du changement de mode
      if (mode === LayerRenderMode.FILL) {
        const plantabilityFillLayer = activeLayers.value.find(
          (layer) =>
            layer.dataType === DataType.PLANTABILITY &&
            layer.visible &&
            layer.renderMode === LayerRenderMode.FILL
        )

        if (plantabilityFillLayer && dataType !== DataType.PLANTABILITY) {
          mapStore.removeLayer(DataType.PLANTABILITY, LayerRenderMode.FILL)
        }
      }

      mapStore.removeLayer(dataType)
      mapStore.addLayerWithMode(dataType, mode)
    }
  } else {
    if (mode === LayerRenderMode.FILL) {
      const plantabilityFillLayer = activeLayers.value.find(
        (layer) =>
          layer.dataType === DataType.PLANTABILITY &&
          layer.visible &&
          layer.renderMode === LayerRenderMode.FILL
      )

      if (plantabilityFillLayer && dataType !== DataType.PLANTABILITY) {
        mapStore.removeLayer(DataType.PLANTABILITY, LayerRenderMode.FILL)
      }
    }

    mapStore.addLayerWithMode(dataType, mode)
  }
}

const getActiveLayerMode = (dataType: DataType): LayerRenderMode | null => {
  const layer = activeLayers.value.find((layer) => layer.dataType === dataType && layer.visible)
  return layer ? layer.renderMode : null
}

const getLayerIcon = (dataType: DataType) => {
  switch (dataType) {
    case DataType.PLANTABILITY:
      return "pi pi-seedling"
    case DataType.VULNERABILITY:
      return "pi pi-sun"
    case DataType.CLIMATE_ZONE:
      return "pi pi-globe"
    default:
      return "pi pi-map"
  }
}

const getAvailableRenderModes = (dataType: DataType): LayerRenderMode[] => {
  const baseModes = (() => {
    switch (dataType) {
      case DataType.CLIMATE_ZONE:
        return [LayerRenderMode.FILL]
      case DataType.VULNERABILITY:
        return [LayerRenderMode.FILL, LayerRenderMode.COLOR_RELIEF]
      case DataType.PLANTABILITY:
        return [LayerRenderMode.FILL, LayerRenderMode.SYMBOL]
      default:
        return [LayerRenderMode.FILL]
    }
  })()

  return baseModes.sort((a, b) => {
    if (a === LayerRenderMode.FILL) return -1
    if (b === LayerRenderMode.FILL) return 1
    return 0
  })
}

const getRenderModeOptions = (dataType: DataType) => {
  return getAvailableRenderModes(dataType).map((mode) => ({
    label: getRenderModeLabel(mode),
    value: mode,
    icon: getRenderModeIcon(mode)
  }))
}

const getRenderModeLabel = (mode: LayerRenderMode): string => {
  switch (mode) {
    case LayerRenderMode.FILL:
      return "Plein"
    case LayerRenderMode.SYMBOL:
      return "Points"
    case LayerRenderMode.COLOR_RELIEF:
      return "Relief couleur"
    default:
      return "Standard"
  }
}

const getRenderModeIcon = (mode: LayerRenderMode): string => {
  switch (mode) {
    case LayerRenderMode.FILL:
      return "pi pi-stop-fill"
    case LayerRenderMode.SYMBOL:
      return "pi pi-map-marker"
    case LayerRenderMode.COLOR_RELIEF:
      return "pi pi-image"
    default:
      return "pi pi-square-fill"
  }
}
</script>
<template>
  <div class="multi-layer-switcher">
    <div class="switcher-header">
      <div class="header-content">
        <h3 class="header-title">
          <i class="header-icon pi pi-layers"></i>
          <span class="header-text">Calques</span>
        </h3>
      </div>
    </div>
    <div class="unified-layer-mode">
      <div class="layers-grid">
        <div v-for="option in availableOptions" :key="option.value" class="layer-section">
          <div class="layer-type-header">
            <button
              :class="{ active: isLayerActive(option.value) }"
              class="layer-toggle-button"
              @click="togglePanel(option.value)"
            >
              <div class="layer-type-info">
                <div class="layer-type-icon">
                  <i :class="getLayerIcon(option.value)"></i>
                </div>
                <div class="layer-type-content">
                  <span class="layer-type-title">{{ option.label }}</span>
                  <span class="layer-type-subtitle">
                    <span v-if="isLayerActive(option.value)" class="current-mode-indicator">
                      • {{ getRenderModeLabel(getActiveLayerMode(option.value)!) }}
                    </span>
                  </span>
                </div>
              </div>
              <div class="layer-type-status">
                <div :class="{ active: isPanelOpen(option.value) }" class="status-badge">
                  <i
                    :class="isPanelOpen(option.value) ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"
                    class="text-xs"
                  ></i>
                </div>
              </div>
            </button>
          </div>

          <div v-if="isPanelOpen(option.value)" class="render-mode-selector">
            <SelectButton
              :model-value="getActiveLayerMode(option.value)"
              :options="getRenderModeOptions(option.value)"
              class="render-mode-select"
              option-disabled="disabled"
              option-label="label"
              option-value="value"
              size="small"
              @update:model-value="(value) => activateLayerWithMode(option.value, value)"
            >
              <template #option="{ option }">
                <div class="render-mode-option-content">
                  <i :class="option.icon"></i>
                  <span>{{ option.label }}</span>
                </div>
              </template>
            </SelectButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";
.multi-layer-switcher {
  @apply bg-white w-full;
  @apply rounded-lg;
  @apply border border-primary-500;
  @apply text-xs;
  min-width: 280px;
  max-width: 320px;
}

/* En-tête compact */
.switcher-header {
  @apply bg-primary-500 text-white;
  @apply p-2;
}

.header-content {
  @apply flex flex-col;
}

.header-title {
  @apply text-sm font-semibold flex items-center gap-2;
}

.header-icon {
  @apply text-sm;
}

.unified-layer-mode {
  @apply p-1;
  @apply flex flex-col gap-1;
}

.layers-grid {
  @apply space-y-1;
}

.layer-section {
  @apply bg-gray-50 rounded p-1;
}

.layer-type-header {
  @apply mb-1;
}

.layer-toggle-button {
  @apply w-full flex items-center justify-between;
  @apply bg-white hover:bg-gray-100;
  @apply border border-gray-200 rounded px-2 py-1;
  @apply transition-colors duration-200;
  @apply cursor-pointer;
}

.layer-toggle-button.active {
  @apply bg-primary-50 border-primary-200;
}

.layer-type-info {
  @apply flex items-center gap-2;
}

.layer-type-icon {
  @apply flex items-center justify-center;
  @apply w-5 h-5 bg-gray-200 rounded;
  @apply text-gray-600 text-xs;
}

.layer-type-content {
  @apply flex-1;
}

.layer-type-title {
  @apply text-xs font-semibold text-gray-900;
}

.layer-type-subtitle {
  @apply text-xs text-gray-600 leading-none;
}

.current-mode-indicator {
  @apply text-primary-600 font-medium;
}

.layer-type-status {
  @apply flex items-center justify-center;
}

.status-badge {
  @apply w-4 h-4 rounded-full flex items-center justify-center;
  @apply transition-all duration-200;
}

.status-badge.active {
  @apply bg-primary-500 text-white;
}

.status-badge:not(.active) {
  @apply bg-gray-300 text-gray-600 hover:bg-gray-400;
}

.mode-activation-prompt {
  @apply p-2 text-center;
}

.prompt-text {
  @apply text-xs text-gray-600 font-medium;
  @apply mb-2;
}

.layer-controls {
  @apply p-2 border-b border-gray-200;
}

.deactivate-button {
  @apply flex items-center gap-2;
  @apply w-full px-3 py-2;
  @apply bg-red-50 hover:bg-red-100;
  @apply border border-red-200 hover:border-red-300;
  @apply text-red-600 hover:text-red-700;
  @apply rounded transition-all duration-200;
  @apply text-xs font-medium;
}

.render-mode-selector {
  @apply mt-1 bg-gray-50 rounded overflow-hidden;
  @apply border border-gray-200;
}
</style>
