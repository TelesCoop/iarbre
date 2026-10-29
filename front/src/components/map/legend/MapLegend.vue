<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToAttributionSource } from "@/utils/enum"

const mapStore = useMapStore()
const FIXED_HEIGHT_DATA_TYPES = [
  DataType.PLANTABILITY,
  DataType.VULNERABILITY,
  DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY
]
const FIXED_WIDTH_DATA_TYPES = [...FIXED_HEIGHT_DATA_TYPES, DataType.CLIMATE_ZONE]
const hasFixedWidth = computed(() => FIXED_WIDTH_DATA_TYPES.includes(mapStore.selectedDataType))
const hasFixedHeight = computed(() => FIXED_HEIGHT_DATA_TYPES.includes(mapStore.selectedDataType))
const attribution = computed(() =>
  mapStore.selectedDataType ? DataTypeToAttributionSource[mapStore.selectedDataType] : null
)
</script>

<template>
  <div
    v-if="mapStore.selectedDataType"
    :class="[
      'legend-panel',
      { 'legend-panel-fixed-width': hasFixedWidth, 'legend-panel-fixed-height': hasFixedHeight }
    ]"
  >
    <PlantabilityLegend v-if="mapStore.selectedDataType === DataType.PLANTABILITY" class="w-full" />
    <ClimateZoneLegend
      v-else-if="mapStore.selectedDataType === DataType.CLIMATE_ZONE"
      class="w-full"
    />
    <VulnerabilityLegend
      v-else-if="mapStore.selectedDataType === DataType.VULNERABILITY"
      class="w-full"
    />
    <PlantVulnerabilityLegend
      v-else-if="mapStore.selectedDataType === DataType.PLANTABILITY_VULNERABILITY"
      class="w-full"
    />
    <biosphere-functional-integrity-legend
      v-else-if="mapStore.selectedDataType === DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY"
      class="w-full"
    />
    <vegetation-legend
      v-else-if="mapStore.selectedDataType === DataType.VEGESTRATE"
      class="w-full"
    />
    <MapFiltersStatus />

    <p v-if="attribution" class="legend-attribution">
      Source :
      <a
        :href="attribution.url"
        class="text-primary-500"
        rel="noopener noreferrer"
        target="_blank"
        >{{ attribution.label }}</a
      >
    </p>
  </div>
</template>
