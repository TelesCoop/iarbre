<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"
import type { PlantabilityVulnerabilityData } from "@/types/vulnerability_plantability"
import type { VegetationData } from "@/types/vegetation"
import AppSpinner from "@/components/shared/AppSpinner.vue"

const mapStore = useMapStore()

defineProps({
  fullHeight: {
    type: Boolean,
    default: false
  }
})
</script>

<template>
  <div class="map-context-data-container w-full flex flex-col min-h-0" data-cy="map-context-data">
    <div v-if="mapStore.isCalculating" class="flex flex-col items-center justify-center gap-4 p-8">
      <AppSpinner size="md" color="#426A45" />
      <div class="text-brown text-center">Calcul en cours...</div>
    </div>
    <template v-else>
      <MapContextDataPlantability
        v-if="mapStore.selectedDataType === DataType.PLANTABILITY"
        :data="mapStore.contextData.data as PlantabilityData"
      />
      <MapContextDataVulnerability
        v-else-if="mapStore.selectedDataType === DataType.VULNERABILITY"
        :data="mapStore.contextData.data as VulnerabilityData"
      />
      <MapContextDataClimateZone
        v-else-if="mapStore.selectedDataType === DataType.CLIMATE_ZONE"
        :data="mapStore.contextData.data as ClimateData"
      />
      <map-context-data-biosphere-integrity
        v-else-if="mapStore.selectedDataType === DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY"
      />
      <MapContextDataPlantabilityVulnerability
        v-else-if="mapStore.selectedDataType === DataType.PLANTABILITY_VULNERABILITY"
        :data="mapStore.contextData.data as PlantabilityVulnerabilityData"
      />
      <map-context-data-vegetation
        v-else-if="mapStore.selectedDataType === DataType.VEGETATION"
        :data="mapStore.contextData.data as VegetationData"
      />
    </template>
  </div>
</template>
