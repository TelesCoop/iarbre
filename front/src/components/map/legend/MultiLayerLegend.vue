<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"
import { computed } from "vue"
import MultiLayerPlantabilityLegend from "@/components/map/legend/MultiLayerPlantabilityLegend.vue"
import MultiLayerVulnerabilityLegend from "@/components/map/legend/MultiLayerVulnerabilityLegend.vue"
import MultiLayerClimateZoneLegend from "@/components/map/legend/MultiLayerClimateZoneLegend.vue"

const mapStore = useMapStore()

const activeLayers = computed(() => mapStore.activeLayers.filter((layer) => layer.visible))

const hasMultipleLayers = computed(() => activeLayers.value.length > 1)
</script>

<template>
  <div v-if="activeLayers.length > 0" class="multi-layer-legend">
    <div class="legend-header">
      <h3 class="legend-title">
        {{ hasMultipleLayers ? "Légendes des calques" : "Légende" }}
      </h3>
    </div>

    <div class="legend-layers">
      <div v-for="layer in activeLayers" :key="layer.dataType" class="legend-layer-container">
        <!-- En-tête du calque avec opacité -->
        <div v-if="hasMultipleLayers" class="layer-info">
          <div class="flex justify-between items-center">
            <span class="layer-title">
              {{ DataTypeToLabel[layer.dataType] }}
            </span>
            <span class="layer-opacity"> {{ Math.round(layer.opacity * 100) }}% </span>
          </div>
        </div>

        <!-- Légende spécifique au type de données -->
        <div class="legend-content" :style="{ opacity: layer.opacity }">
          <MultiLayerPlantabilityLegend
            v-if="layer.dataType === DataType.PLANTABILITY"
            :data-type="layer.dataType"
          />
          <MultiLayerVulnerabilityLegend
            v-else-if="layer.dataType === DataType.VULNERABILITY"
            :data-type="layer.dataType"
          />
          <MultiLayerClimateZoneLegend
            v-else-if="layer.dataType === DataType.CLIMATE_ZONE"
            :data-type="layer.dataType"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.multi-layer-legend {
  background-color: white;
  border-radius: 12px;
  padding: 1rem;
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  min-width: 200px;
  max-width: 320px;
}

.legend-header {
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
  margin: -1rem -1rem 0.75rem -1rem;
  padding: 0.75rem 1rem;
  border-radius: 12px 12px 0 0;
}

.legend-layers {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.legend-layer-container {
  position: relative;
}

.layer-info {
  margin-bottom: 0.5rem;
  padding: 0.75rem;
  background-color: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  border-left: 3px solid #3b82f6;
}

.legend-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.layer-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #374151;
  line-height: 1.25;
}

.layer-opacity {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
  font-family: "SF Mono", "Monaco", "Inconsolata", "Roboto Mono", monospace;
}

.legend-content {
  transition: opacity 0.2s ease-in-out;
}

/* Ajustements pour les légendes dans un contexte multi-calques */
.legend-layer-container :deep(.legend-container) {
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
  margin: 0;
}

.legend-layer-container :deep(.legend-title) {
  display: none; /* Cacher le titre individuel car on a le titre du calque */
}
</style>
