<script lang="ts" setup>
import { ref, watch } from "vue"
import { useMapStore } from "@/stores/map"
import { DataType, getDataTypeAttributionSource } from "@/utils/enum"

const mapStore = useMapStore()
const attributionHTML = ref("")

watch(
  () => mapStore.selectedDataType,
  async (dataType) => {
    if (dataType) {
      attributionHTML.value = await getDataTypeAttributionSource(dataType)
    }
  },
  { immediate: true }
)
</script>

<template>
  <div v-if="mapStore.selectedDataType" class="legend-panel">
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
    <p v-if="attributionHTML" class="legend-attribution">
      Source : <span v-html="attributionHTML" />
    </p>
  </div>
</template>
