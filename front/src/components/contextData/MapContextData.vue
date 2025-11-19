<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"
import type { PlantabilityVulnerabilityData } from "@/types/vulnerability_plantability"
import CompactContextData from "./CompactContextData.vue"
import MapContextDataPlantability from "./MapContextDataPlantability.vue"
import MapContextDataVulnerability from "./MapContextDataVulnerability.vue"
import MapContextDataClimateZone from "./MapContextDataClimateZone.vue"
import MapContextDataPlantabilityVulnerability from "./MapContextDataPlantabilityVulnerability.vue"
import { Button } from "primevue"

const mapStore = useMapStore()

defineProps({
  fullHeight: {
    type: Boolean,
    default: false
  }
})

// Extract current data
const currentData = computed(() => mapStore.contextData.currentContextData?.data || null)

// Check if current item is already in selected list
const isCurrentInSelected = computed(() => {
  if (!mapStore.contextData.currentContextData) return false
  const currentId = mapStore.contextData.currentContextData.data.id
  return mapStore.contextData.selectedContextData.some((item) => item.data.id === currentId)
})

// Handle remove from selected list
const handleRemove = (id: string) => {
  mapStore.contextData.removeData(id)
}

// Handle add to selected list
const handleAddToSelected = () => {
  mapStore.contextData.addCurrentToSelected()
}
</script>

<template>
  <div class="map-context-data-container w-full" data-cy="map-context-data">
    <!-- Current context data - displayed in full -->
    <div v-if="currentData">
      <div class="mb-3">
        <map-context-data-plantability
          v-if="mapStore.selectedDataType === DataType.PLANTABILITY"
          :data="currentData as PlantabilityData"
        />
        <map-context-data-vulnerability
          v-if="mapStore.selectedDataType === DataType.VULNERABILITY"
          :data="currentData as VulnerabilityData"
        />
        <map-context-data-climate-zone
          v-if="mapStore.selectedDataType === DataType.CLIMATE_ZONE"
          :data="currentData as ClimateData"
        />
        <map-context-data-plantability-vulnerability
          v-if="mapStore.selectedDataType === DataType.PLANTABILITY_VULNERABILITY"
          :data="currentData as PlantabilityVulnerabilityData"
        />
      </div>

      <!-- Add to list button -->
      <div class="mb-4 flex justify-center">
        <Button
          label="Ajouter à la liste"
          icon="pi pi-plus"
          severity="secondary"
          outlined
          size="small"
          :disabled="isCurrentInSelected"
          class="w-full"
          @click="handleAddToSelected"
        />
      </div>
    </div>

    <!-- Selected context data - displayed in compact format -->
    <div v-if="mapStore.contextData.selectedContextData.length > 0" class="mt-4">
      <h3 class="text-sm font-semibold text-gray-700 mb-2">Données sélectionnées</h3>
      <div class="space-y-2">
        <CompactContextData
          v-for="item in mapStore.contextData.selectedContextData"
          :key="item.data.id"
          :item="item"
          @remove="handleRemove"
        />
      </div>
    </div>
  </div>
</template>
