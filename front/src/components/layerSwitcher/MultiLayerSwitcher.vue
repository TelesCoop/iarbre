<template>
  <div class="multi-layer-switcher">
    <!-- En-tête - Style exact du map context panel -->
    <div class="switcher-header">
      <div class="header-content">
        <h3 class="header-title">
          <i class="header-icon pi pi-layers"></i>
          <span class="header-text">Gestion des calques</span>
        </h3>
        <div class="header-subtitle">
          <i class="pi pi-info-circle mr-2"></i>
          {{ isMultiLayerMode ? "Mode avancé activé" : "Mode simple activé" }}
        </div>
      </div>

      <!-- Toggle entre modes -->
      <div class="mode-toggle">
        <button
          :class="{ active: !isMultiLayerMode }"
          class="toggle-button"
          @click="isMultiLayerMode && toggleMode()"
        >
          <i class="pi pi-eye"></i>
          <span>Simple</span>
        </button>
        <button
          :class="{ active: isMultiLayerMode }"
          class="toggle-button"
          @click="!isMultiLayerMode && toggleMode()"
        >
          <i class="pi pi-layers"></i>
          <span>Multi</span>
        </button>
      </div>
    </div>

    <!-- Mode mono-calque -->
    <div v-if="!isMultiLayerMode" class="single-layer-mode">
      <div class="mode-card">
        <div class="mode-card-header">
          <i class="pi pi-eye"></i>
          <span class="mode-card-title">Calque unique</span>
        </div>
        <div class="p-2 sm:p-4">
          <Select
            v-model="selectedSingleLayer"
            :options="availableOptions"
            class="w-full modern-select"
            option-label="label"
            option-value="value"
            placeholder="Choisir un calque"
          />
        </div>
      </div>
    </div>

    <!-- Mode multi-calques -->
    <div v-else class="multi-layer-mode">
      <!-- Sélection des calques disponibles -->
      <div class="mode-card">
        <div class="mode-card-header">
          <i class="pi pi-plus-circle"></i>
          <span class="mode-card-title">Ajouter des calques</span>
        </div>
        <div class="available-layers-grid">
          <button
            v-for="option in availableOptions"
            :key="option.value"
            :class="{
              active: isLayerActive(option.value),
              disabled: !isLayerActive(option.value) && activeLayers.length >= 3
            }"
            :disabled="!isLayerActive(option.value) && activeLayers.length >= 3"
            class="layer-option"
            @click="toggleLayer(option.value)"
          >
            <div class="layer-option-icon">
              <i :class="getLayerIcon(option.value)"></i>
            </div>
            <div class="layer-option-content">
              <span class="layer-option-title">{{ option.label }}</span>
              <span class="layer-option-subtitle">{{ getLayerDescription(option.value) }}</span>
            </div>
            <div class="layer-option-status">
              <i
                :class="isLayerActive(option.value) ? 'pi pi-check-circle' : 'pi pi-plus-circle'"
              ></i>
            </div>
          </button>
        </div>
      </div>

      <!-- Calques actifs avec contrôles -->
      <div v-if="activeLayers.length > 0" class="mode-card">
        <div class="mode-card-header">
          <i class="pi pi-cog"></i>
          <span class="mode-card-title">
            Calques actifs ({{ activeLayers.filter((l) => l.visible).length }}/{{
              activeLayers.length
            }})
          </span>
        </div>

        <div class="active-layers-list">
          <div
            v-for="(layer, index) in activeLayers"
            :key="layer.dataType"
            :style="{ '--layer-index': index }"
            class="layer-control"
          >
            <!-- En-tête du calque -->
            <div class="layer-control-header">
              <div class="layer-info">
                <div :class="getLayerClass(layer.dataType)" class="layer-indicator">
                  <div class="indicator-dot"></div>
                </div>
                <div class="layer-details">
                  <span class="layer-name">{{ DataTypeToLabel[layer.dataType] }}</span>
                  <span class="layer-desc">{{ getLayerDescription(layer.dataType) }}</span>
                </div>
              </div>

              <div class="layer-actions">
                <button
                  :class="{ active: layer.visible }"
                  :title="layer.visible ? 'Masquer le calque' : 'Afficher le calque'"
                  class="action-button visibility-button"
                  @click="toggleLayerVisibility(layer.dataType)"
                >
                  <i :class="layer.visible ? 'pi pi-eye' : 'pi pi-eye-slash'"></i>
                </button>
                <button
                  class="action-button remove-button"
                  title="Supprimer le calque"
                  @click="removeLayer(layer.dataType)"
                >
                  <i class="pi pi-trash"></i>
                </button>
              </div>
            </div>

            <!-- Contrôle d'opacité -->
            <div v-if="layer.visible" class="opacity-control">
              <div class="opacity-header">
                <i class="pi pi-circle opacity-icon"></i>
                <span class="opacity-label">Opacité</span>
                <span class="opacity-value">{{ Math.round(layer.opacity * 100) }}%</span>
              </div>
              <div class="opacity-slider-container">
                <Slider
                  v-model="layer.opacity"
                  :max="1"
                  :min="0"
                  :step="0.05"
                  class="opacity-slider"
                  @update:model-value="
                    (value) => updateLayerOpacity(layer.dataType, value as number)
                  "
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed, ref } from "vue"
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"
import Button from "primevue/button"
import Select from "primevue/select"
import Slider from "primevue/slider"

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

const isMultiLayerMode = computed(() => mapStore.isMultiLayerMode)
const activeLayers = computed(() => mapStore.activeLayers)
const visibleLayers = computed(() => activeLayers.value.filter((layer) => layer.visible))

// Gestion du mode mono-calque
const selectedSingleLayer = computed({
  get: () => mapStore.selectedDataType,
  set: (value: DataType) => {
    mapStore.changeDataType(value)
  }
})

const toggleMode = () => {
  mapStore.toggleMultiLayerMode()
}

const isLayerActive = (dataType: DataType) => {
  return activeLayers.value.some((layer) => layer.dataType === dataType && layer.visible)
}

const toggleLayer = (dataType: DataType) => {
  const existingLayer = activeLayers.value.find((layer) => layer.dataType === dataType)

  if (existingLayer) {
    if (existingLayer.visible) {
      // Si le calque est visible, le cacher ou le supprimer
      if (activeLayers.value.filter((l) => l.visible).length > 1) {
        mapStore.toggleLayerVisibility(dataType)
      } else {
        mapStore.removeLayer(dataType)
      }
    } else {
      // Si le calque existe mais n'est pas visible, le rendre visible
      mapStore.toggleLayerVisibility(dataType)
    }
  } else {
    // Ajouter un nouveau calque
    mapStore.addLayer(dataType)
  }
}

const toggleLayerVisibility = (dataType: DataType) => {
  mapStore.toggleLayerVisibility(dataType)
}

const removeLayer = (dataType: DataType) => {
  mapStore.removeLayer(dataType)
}

const updateLayerOpacity = (dataType: DataType, opacity: number) => {
  mapStore.setLayerOpacity(dataType, opacity)
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

const getLayerDescription = (dataType: DataType) => {
  switch (dataType) {
    case DataType.PLANTABILITY:
      return "Potentiel de plantation"
    case DataType.VULNERABILITY:
      return "Risque de chaleur"
    case DataType.CLIMATE_ZONE:
      return "Zone climatique locale"
    default:
      return ""
  }
}

const getLayerClass = (dataType: DataType) => {
  switch (dataType) {
    case DataType.PLANTABILITY:
      return "plantability"
    case DataType.VULNERABILITY:
      return "vulnerability"
    case DataType.CLIMATE_ZONE:
      return "climate-zone"
    default:
      return ""
  }
}
</script>

<style scoped>
@reference "@/styles/main.css";
.multi-layer-switcher {
  @apply bg-white w-full max-w-full;
  @apply transition-all duration-200;
  @apply rounded-lg;
  @apply border border-primary-500;
  min-width: 320px;
  max-width: 380px;
  overflow: hidden;
}

/* En-tête - Style exact du map context panel */
.switcher-header {
  @apply bg-primary-500 text-white relative;
  @apply p-2 md:p-4;
}

.header-content {
  @apply pr-4;
}

.header-icon {
  @apply inline-flex mr-2;
}

.header-text {
  @apply inline;
}

.header-title {
  @apply mb-2;
}

.header-subtitle {
  @apply text-xs;
  @apply flex items-center;
}

/* Toggle modes - Style simplifié */
.mode-toggle {
  @apply flex gap-2 mt-2;
}

.toggle-button {
  @apply flex-1 px-3 py-2 text-xs font-medium;
  @apply bg-white/20 hover:bg-white/30;
  @apply border border-white/30 rounded;
  @apply text-white cursor-pointer;
  @apply transition-colors duration-200;
  @apply flex items-center justify-center gap-1;
}

.toggle-button.active {
  @apply bg-white/40 font-semibold;
}

.toggle-button:disabled {
  @apply opacity-50 cursor-not-allowed;
}

/* Contenu des modes - Style du context panel */
.single-layer-mode,
.multi-layer-mode {
  @apply p-1 sm:p-2 md:p-4;
  @apply flex flex-col gap-1 sm:gap-2 md:gap-4;
  @apply text-xs min-h-0;
}

/* Cartes de mode - Style context panel */
.mode-card {
  @apply bg-white rounded-lg border-0;
  @apply mb-2;
}

.mode-card-header {
  @apply bg-gray-200 border-b border-gray-200;
  @apply px-2 sm:px-4 py-2 sm:py-4;
  @apply shadow-sm;
  @apply flex items-center gap-2;
}

.mode-card-title {
  @apply text-xs font-bold text-gray-700 uppercase tracking-wider;
}

/* Sélection */
.modern-select {
  @apply mt-2;
}

/* Grille des calques disponibles */
.available-layers-grid {
  @apply p-2 sm:p-4;
  @apply grid gap-2;
}

.layer-option {
  @apply bg-gray-50 hover:bg-gray-100 focus-within:bg-gray-100;
  @apply transition-colors duration-200;
  @apply cursor-pointer;
  @apply border-0 rounded p-2 sm:p-3;
  @apply flex items-center gap-3;
  @apply text-left;
}

.layer-option:hover {
  @apply bg-gray-100;
}

.layer-option.active {
  @apply bg-primary-100;
}

.layer-option.disabled {
  @apply opacity-50 cursor-not-allowed;
}

.layer-option.disabled:hover {
  @apply bg-gray-50;
}

.layer-option-icon {
  @apply flex items-center justify-center;
  @apply w-8 h-8 bg-gray-200 rounded;
  @apply text-gray-600;
}

.layer-option.active .layer-option-icon {
  @apply bg-primary-500 text-white;
}

.layer-option-content {
  @apply flex-1;
}

.layer-option-title {
  @apply text-xs font-semibold text-gray-900;
  @apply mb-1;
}

.layer-option-subtitle {
  @apply text-xs text-gray-600;
}

.layer-option-status {
  @apply flex items-center justify-center;
  @apply text-gray-500;
}

.layer-option.active .layer-option-status {
  @apply text-primary-600;
}

/* Liste des calques actifs */
.active-layers-list {
  @apply p-2 sm:p-4;
  @apply flex flex-col gap-2;
}

.layer-control {
  @apply bg-gray-50 hover:bg-gray-100;
  @apply transition-colors duration-200;
  @apply rounded p-2 sm:p-3;
  animation: slideIn 0.4s ease calc(var(--layer-index) * 0.1s) both;
}

.layer-control:hover {
  @apply bg-gray-100;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.layer-control-header {
  @apply flex justify-between items-center;
  @apply mb-2;
}

.layer-info {
  @apply flex items-center gap-3 flex-1;
}

.layer-indicator {
  @apply relative flex items-center justify-center;
  @apply w-6 h-6;
}

.indicator-dot {
  @apply w-3 h-3 rounded-full;
  @apply relative z-10;
}

.layer-indicator.plantability .indicator-dot {
  background: linear-gradient(135deg, #10b981, #059669);
}

.layer-indicator.vulnerability .indicator-dot {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.layer-indicator.climate-zone .indicator-dot {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.layer-details {
  @apply flex-1;
}

.layer-name {
  @apply text-xs font-semibold text-gray-900;
  @apply block mb-1;
}

.layer-desc {
  @apply text-xs text-gray-600;
}

.layer-actions {
  @apply flex items-center gap-2;
}

.action-button {
  @apply bg-gray-200 hover:bg-gray-300;
  @apply border-0 rounded p-1;
  @apply cursor-pointer;
  @apply transition-colors duration-200;
  @apply flex items-center justify-center;
  @apply w-7 h-7;
  @apply text-gray-600;
}

.visibility-button.active {
  @apply bg-primary-500 text-white;
}

.remove-button:hover {
  @apply bg-red-500 text-white;
}

/* Contrôle d'opacité */
.opacity-control {
  @apply bg-gray-100 rounded p-3 mt-2;
}

.opacity-header {
  @apply flex items-center justify-between mb-2;
}

.opacity-icon {
  @apply text-gray-500 text-xs;
}

.opacity-label {
  @apply text-xs text-gray-600 ml-2 flex-1;
}

.opacity-value {
  @apply text-xs font-semibold text-gray-900;
  @apply font-mono;
}

.opacity-slider-container {
  @apply mt-2;
}

/* Personnalisation du slider PrimeVue */
:deep(.p-slider) {
  background: #e5e7eb;
  border-radius: 6px;
  height: 6px;
}

:deep(.p-slider .p-slider-range) {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 6px;
}

:deep(.p-slider .p-slider-handle) {
  border: 2px solid #3b82f6;
  background: white;
  width: 18px;
  height: 18px;
  margin-left: -9px;
  margin-top: -6px;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

:deep(.p-slider .p-slider-handle:hover) {
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

/* Personnalisation du Select PrimeVue */
:deep(.p-select) {
  border-radius: 8px;
  border-color: #e2e8f0;
}

:deep(.p-select:hover) {
  border-color: #cbd5e1;
}

:deep(.p-select:focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Responsive */
@media (max-width: 480px) {
  .multi-layer-switcher {
    min-width: 280px;
    max-width: 320px;
  }

  .switcher-header {
    padding: 1.25rem;
  }

  .single-layer-mode,
  .multi-layer-mode {
    padding: 1.25rem;
  }

  .layer-option {
    padding: 0.75rem;
  }

  .layer-control {
    padding: 0.75rem;
  }
}
</style>
