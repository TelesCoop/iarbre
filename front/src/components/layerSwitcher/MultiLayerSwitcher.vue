<script lang="ts" setup>
import { computed } from "vue"
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

const isLayerActive = (dataType: DataType) => {
  return activeLayers.value.some((layer) => layer.dataType === dataType && layer.visible)
}

const toggleLayerType = (dataType: DataType) => {
  const existingLayer = activeLayers.value.find(
    (layer) => layer.dataType === dataType && layer.visible
  )

  if (existingLayer) {
    // Si le calque est actif, le supprimer
    mapStore.removeLayer(dataType)
  } else {
    // Ajouter le calque avec le mode par défaut
    const defaultMode = getDefaultRenderMode(dataType)
    mapStore.addLayerWithMode(dataType, defaultMode)
  }
}

const changeLayerMode = (dataType: DataType, newMode: LayerRenderMode) => {
  const existingLayer = activeLayers.value.find(
    (layer) => layer.dataType === dataType && layer.visible
  )

  if (existingLayer && existingLayer.renderMode !== newMode) {
    // Si on veut passer en mode FILL, vérifier que c'est autorisé
    if (newMode === LayerRenderMode.FILL && !canUseFillMode(dataType)) {
      // Ne rien faire si le mode FILL n'est pas disponible
      return
    }

    // Changer le mode du calque actuel
    mapStore.removeLayer(dataType)
    mapStore.addLayerWithMode(dataType, newMode)
  }
}

const getActiveLayerMode = (dataType: DataType): LayerRenderMode | null => {
  const layer = activeLayers.value.find((layer) => layer.dataType === dataType && layer.visible)
  return layer ? layer.renderMode : null
}

const getDefaultRenderMode = (dataType: DataType): LayerRenderMode => {
  const hasFillLayer = activeLayers.value.some(
    (layer) =>
      layer.visible && layer.renderMode === LayerRenderMode.FILL && layer.dataType !== dataType
  )

  if (hasFillLayer) {
    switch (dataType) {
      case DataType.PLANTABILITY:
        return LayerRenderMode.SYMBOL
      case DataType.VULNERABILITY:
        return LayerRenderMode.HEATMAP
      case DataType.CLIMATE_ZONE:
        return LayerRenderMode.FILL
      default:
        return LayerRenderMode.FILL
    }
  }

  // Sinon, utiliser le mode FILL par défaut
  return LayerRenderMode.FILL
}

const canUseFillMode = (dataType: DataType): boolean => {
  // Peut utiliser FILL si :
  // 1. C'est le calque actuel qui est déjà en mode FILL, OU
  // 2. Aucun autre calque n'utilise le mode FILL
  const currentLayer = activeLayers.value.find(
    (layer) => layer.dataType === dataType && layer.visible
  )

  // Si le calque actuel est déjà en mode FILL, on peut le garder
  if (currentLayer && currentLayer.renderMode === LayerRenderMode.FILL) {
    return true
  }

  // Sinon, vérifier qu'aucun autre calque n'utilise FILL
  return !activeLayers.value.some(
    (layer) =>
      layer.visible && layer.renderMode === LayerRenderMode.FILL && layer.dataType !== dataType
  )
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
        return [LayerRenderMode.FILL, LayerRenderMode.HEATMAP]
      case DataType.PLANTABILITY:
        return [LayerRenderMode.FILL, LayerRenderMode.SYMBOL]
      default:
        return [LayerRenderMode.FILL]
    }
  })()

  // Réorganiser pour que FILL soit toujours en premier, même s'il y a conflit
  // Cela permet de voir visuellement l'état de conflit
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
    icon: getRenderModeIcon(mode),
    disabled:
      mode === LayerRenderMode.FILL &&
      !canUseFillMode(dataType) &&
      getActiveLayerMode(dataType) !== LayerRenderMode.FILL
  }))
}

const getRenderModeLabel = (mode: LayerRenderMode): string => {
  switch (mode) {
    case LayerRenderMode.FILL:
      return "Plein"
    case LayerRenderMode.PATTERN:
      return "Motifs"
    case LayerRenderMode.SYMBOL:
      return "Points"
    case LayerRenderMode.HEATMAP:
      return "Chaleur"
    case LayerRenderMode.HILLSHADE:
      return "Ombré"
    default:
      return "Standard"
  }
}

const getRenderModeIcon = (mode: LayerRenderMode): string => {
  switch (mode) {
    case LayerRenderMode.FILL:
      return "pi pi-stop-fill"
    case LayerRenderMode.PATTERN:
      return "pi pi-th"
    case LayerRenderMode.SYMBOL:
      return "pi pi-map-marker"
    case LayerRenderMode.HEATMAP:
      return "pi pi-chart-scatter"
    case LayerRenderMode.HILLSHADE:
      return "pi pi-sun"
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
          <!-- En-tête du type de calque avec toggle -->
          <div class="layer-type-header">
            <button
              :class="{ active: isLayerActive(option.value) }"
              class="layer-toggle-button"
              @click="toggleLayerType(option.value)"
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
                <div v-if="isLayerActive(option.value)" class="status-badge active">
                  <i class="pi pi-check text-xs"></i>
                </div>
                <div v-else class="status-badge inactive">
                  <i class="pi pi-plus text-xs"></i>
                </div>
              </div>
            </button>
          </div>

          <!-- Sélecteur de mode de rendu avec SelectButton (visible seulement si calque actif et multiple modes) -->
          <div
            v-if="isLayerActive(option.value) && getAvailableRenderModes(option.value).length > 1"
            class="render-mode-selector"
          >
            <SelectButton
              :model-value="getActiveLayerMode(option.value)"
              :options="getRenderModeOptions(option.value)"
              class="render-mode-select"
              option-disabled="disabled"
              option-label="label"
              option-value="value"
              @update:model-value="(value) => changeLayerMode(option.value, value)"
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

.header-subtitle {
  @apply text-xs opacity-90 mt-1;
}

/* Contenu unifié - Style compact */
.unified-layer-mode {
  @apply p-1;
  @apply flex flex-col gap-1;
}

/* Grille des calques avec modes de rendu */
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

.status-badge.inactive {
  @apply bg-gray-300 text-gray-600 hover:bg-gray-400;
}

.render-mode-selector {
  @apply mt-1 bg-gray-50 rounded overflow-hidden;
  @apply border border-gray-200;
}

/* Personnalisation du SelectButton PrimeVue */
.render-mode-select {
  @apply w-full;
}

:deep(.p-selectbutton) {
  @apply w-full;
}

:deep(.p-selectbutton .p-button) {
  @apply flex-1 py-1 px-2 text-xs;
  @apply border-gray-200;
  min-height: auto;
}

:deep(.p-selectbutton .p-button:not(.p-highlight)) {
  @apply bg-white text-gray-700;
}

:deep(.p-selectbutton .p-button.p-highlight) {
  @apply bg-primary-50 text-primary-700 border-primary-200;
}

:deep(.p-selectbutton .p-button:disabled) {
  @apply bg-gray-100 text-gray-400 cursor-not-allowed opacity-60;
}

.render-mode-option-content {
  @apply flex items-center gap-1;
}

.render-mode-option-content i {
  @apply text-xs;
}

.render-mode-option-content span {
  @apply text-xs;
}
</style>
