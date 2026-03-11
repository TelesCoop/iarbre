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
    <vegetation-legend
      v-else-if="mapStore.selectedDataType === DataType.VEGESTRATE"
      class="w-full"
    />
    <p v-if="attributionHTML" class="attribution">Source : <span v-html="attributionHTML" /></p>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.legend-panel {
  @apply flex flex-col justify-center items-center;
  @apply gap-1 py-1.5 px-2;
  @apply bg-white border border-gray-200 rounded-lg;
  @apply text-xs text-gray-700 font-sans;
}

.attribution {
  @apply w-full text-center text-gray-500 pt-1 border-t border-gray-100;
}

@media (min-width: 1024px) {
  .legend-panel {
    @apply gap-2 py-2 px-3 text-sm;
  }
}
</style>
