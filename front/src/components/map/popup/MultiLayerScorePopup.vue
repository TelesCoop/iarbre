<template>
  <div
    v-if="
      multiLayerPopupData && multiLayerPopupData.layers && multiLayerPopupData.layers.length > 0
    "
    class="multi-layer-popup"
    data-cy="multi-layer-score-popup"
  >
    <!-- En-tête moderne avec gradient -->
    <div class="popup-header">
      <div class="header-content">
        <div class="title-section">
          <div class="layers-badge">
            <i class="pi pi-layers text-white text-xs"></i>
            <span class="badge-text">{{ multiLayerPopupData.layers.length }}</span>
          </div>
          <div class="title-text">
            <h3 class="main-title">Données multi-calques</h3>
            <p class="subtitle">
              {{ multiLayerPopupData.layers.length }} calque{{
                multiLayerPopupData.layers.length > 1 ? "s" : ""
              }}
              actif{{ multiLayerPopupData.layers.length > 1 ? "s" : "" }}
            </p>
          </div>
        </div>

        <button
          class="coords-button"
          data-cy="copy-coords-button"
          :title="`Copier les coordonnées: ${coords}`"
          @click="copy(coords)"
        >
          <i class="pi pi-map-marker text-xs"></i>
          <span class="coords-text">{{ coords }}</span>
          <i class="pi pi-copy text-xs copy-icon"></i>
        </button>
      </div>
    </div>

    <!-- Contenu des calques avec design amélioré -->
    <div class="layers-content">
      <div
        v-for="(layerData, index) in multiLayerPopupData.layers"
        :key="layerData.dataType"
        class="layer-card"
        :style="{ '--layer-index': index }"
      >
        <!-- En-tête du calque avec indicateur visuel -->
        <div class="layer-header">
          <div class="layer-title-section">
            <div :class="getLayerIndicatorClass(layerData.dataType)" class="layer-indicator">
              <div class="indicator-dot"></div>
              <div class="indicator-ring"></div>
            </div>
            <div class="layer-info">
              <h4 class="layer-title">{{ DataTypeToLabel[layerData.dataType] }}</h4>
              <p class="layer-subtitle">{{ getLayerSubtitle(layerData.dataType) }}</p>
            </div>
          </div>
          <div class="layer-score-preview">
            {{ getScorePreview(layerData) }}
          </div>
        </div>

        <!-- Contenu spécifique au type de données -->
        <div class="layer-content">
          <PlantabilityScorePopupContent
            v-if="layerData.dataType === DataType.PLANTABILITY"
            :popup-data="transformToPopupData(layerData)"
          />
          <ClimateZoneScorePopupContent
            v-else-if="layerData.dataType === DataType.CLIMATE_ZONE"
            :popup-data="transformToPopupData(layerData)"
          />
          <VulnerabilityScorePopupContent
            v-else-if="layerData.dataType === DataType.VULNERABILITY"
            :popup-data="transformToPopupData(layerData)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"
import { copyToClipboard } from "@/utils/clipboard"
import { useToast } from "primevue/usetoast"
import type { LayerPopupData, MapScorePopupData } from "@/types/map"

import PlantabilityScorePopupContent from "@/components/map/popup/PlantabilityScorePopupContent.vue"
import ClimateZoneScorePopupContent from "@/components/map/popup/ClimateZoneScorePopupContent.vue"
import VulnerabilityScorePopupContent from "@/components/map/popup/VulnerabilityScorePopupContent.vue"

const mapStore = useMapStore()
const toast = useToast()

const multiLayerPopupData = computed(() => mapStore.multiLayerPopupData)

const coords = computed(() => {
  if (!multiLayerPopupData.value) return ""
  return `${multiLayerPopupData.value.lat.toFixed(5)}° N, ${multiLayerPopupData.value.lng.toFixed(5)}° E`
})

const copy = (text: string) => {
  copyToClipboard(text)
  toast.add({
    severity: "success",
    summary: "Coordonnées copiées",
    life: 3000,
    group: "br"
  })
}

const transformToPopupData = (layerData: LayerPopupData): MapScorePopupData => {
  const popupData = multiLayerPopupData.value
  if (!popupData) {
    throw new Error("multiLayerPopupData is not available")
  }

  return {
    id: layerData.id,
    lng: popupData.lng,
    lat: popupData.lat,
    properties: layerData.properties,
    score: layerData.score
  }
}

const getLayerIndicatorClass = (dataType: DataType) => {
  const baseClass = "layer-indicator"
  switch (dataType) {
    case DataType.PLANTABILITY:
      return `${baseClass} plantability`
    case DataType.VULNERABILITY:
      return `${baseClass} vulnerability`
    case DataType.CLIMATE_ZONE:
      return `${baseClass} climate-zone`
    default:
      return baseClass
  }
}

const getLayerSubtitle = (dataType: DataType) => {
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

const getScorePreview = (layerData: LayerPopupData) => {
  switch (layerData.dataType) {
    case DataType.PLANTABILITY:
      return `${layerData.score}/10`
    case DataType.VULNERABILITY:
      return `${layerData.score}/9`
    case DataType.CLIMATE_ZONE:
      return `LCZ ${layerData.score}`
    default:
      return layerData.score
  }
}
</script>

<style scoped>
.multi-layer-popup {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  min-width: 320px;
  max-width: 420px;
  backdrop-filter: blur(8px);
}

/* En-tête moderne avec gradient */
.popup-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem 1.25rem;
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.layers-badge {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(8px);
  border-radius: 12px;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 2.5rem;
  height: 2.5rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.badge-text {
  font-size: 0.875rem;
  font-weight: 700;
  margin-left: 0.25rem;
}

.title-text {
  flex: 1;
}

.main-title {
  font-size: 1.125rem;
  font-weight: 700;
  margin: 0;
  line-height: 1.2;
}

.subtitle {
  font-size: 0.875rem;
  margin: 0.25rem 0 0 0;
  opacity: 0.9;
  line-height: 1.3;
}

.coords-button {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  padding: 0.5rem 0.75rem;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  white-space: nowrap;
}

.coords-button:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
}

.coords-text {
  font-family: "SF Mono", "Monaco", "Inconsolata", "Roboto Mono", monospace;
}

.copy-icon {
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.coords-button:hover .copy-icon {
  opacity: 1;
}

/* Contenu des calques */
.layers-content {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.layer-card {
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  transition: all 0.2s ease;
  animation: slideIn 0.4s ease calc(var(--layer-index) * 0.1s) both;
}

.layer-card:hover {
  border-color: #d1d5db;
  box-shadow:
    0 1px 3px 0 rgba(0, 0, 0, 0.1),
    0 1px 2px 0 rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
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

.layer-header {
  padding: 0.75rem 1rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.layer-title-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.layer-indicator {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
}

.indicator-dot {
  width: 1rem;
  height: 1rem;
  border-radius: 50%;
  z-index: 2;
  position: relative;
}

.indicator-ring {
  position: absolute;
  width: 2rem;
  height: 2rem;
  border: 2px solid currentColor;
  border-radius: 50%;
  opacity: 0.3;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.1;
  }
}

.layer-indicator.plantability {
  color: #10b981;
}

.layer-indicator.plantability .indicator-dot {
  background: linear-gradient(135deg, #10b981, #059669);
}

.layer-indicator.vulnerability {
  color: #ef4444;
}

.layer-indicator.vulnerability .indicator-dot {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.layer-indicator.climate-zone {
  color: #3b82f6;
}

.layer-indicator.climate-zone .indicator-dot {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.layer-info {
  flex: 1;
}

.layer-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
  line-height: 1.3;
}

.layer-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0.125rem 0 0 0;
  line-height: 1.3;
}

.layer-score-preview {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 0.375rem 0.625rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #374151;
  font-family: "SF Mono", "Monaco", "Inconsolata", "Roboto Mono", monospace;
}

.layer-content {
  padding: 1rem;
  background: white;
}

/* Ajustements pour les sous-composants */
.layer-content :deep(.score-popup-content) {
  background: transparent;
  border: none;
  padding: 0;
  margin: 0;
}

.layer-content :deep(.popup-coords) {
  display: none;
}

.layer-content :deep(.flex.w-full.flex-col) {
  display: none;
}

/* Responsive */
@media (max-width: 480px) {
  .multi-layer-popup {
    min-width: 280px;
    max-width: 340px;
  }

  .header-content {
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }

  .coords-button {
    align-self: flex-end;
  }
}
</style>
