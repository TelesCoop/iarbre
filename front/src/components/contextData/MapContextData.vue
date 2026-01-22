<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"
import type { PlantabilityVulnerabilityData } from "@/types/vulnerability_plantability"
import type { VegetationData } from "@/types/vegetation"
import ProgressSpinner from "primevue/progressspinner"

const mapStore = useMapStore()

defineProps({
  fullHeight: {
    type: Boolean,
    default: false
  }
})
</script>

<template>
  <div class="map-context-data-container w-full" data-cy="map-context-data">
    <div v-if="mapStore.isCalculating" class="flex flex-col items-center justify-center gap-3 p-8">
      <ProgressSpinner style="width: 50px; height: 50px" stroke-width="4" animation-duration="1s" />
      <div class="text-brown text-center">Calcul en cours...</div>
    </div>
    <template v-else>
      <map-context-data-plantability
        v-if="mapStore.selectedDataType === DataType.PLANTABILITY"
        :data="mapStore.contextData.data as PlantabilityData"
      />
      <map-context-data-vulnerability
        v-else-if="mapStore.selectedDataType === DataType.VULNERABILITY"
        :data="mapStore.contextData.data as VulnerabilityData"
      />
      <map-context-data-climate-zone
        v-else-if="mapStore.selectedDataType === DataType.CLIMATE_ZONE"
        :data="mapStore.contextData.data as ClimateData"
      />
      <map-context-data-plantability-vulnerability
        v-else-if="mapStore.selectedDataType === DataType.PLANTABILITY_VULNERABILITY"
        :data="mapStore.contextData.data as PlantabilityVulnerabilityData"
      />
      <map-context-data-biosphere-integrity
        v-else-if="mapStore.selectedDataType === DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY"
        :data="mapStore.contextData.data as PlantabilityVulnerabilityData"
      />
      <map-context-data-vegetation
        v-if="mapStore.selectedDataType === DataType.VEGETATION"
        :data="mapStore.contextData.data as VegetationData"
      />
    </template>
  </div>
</template>
