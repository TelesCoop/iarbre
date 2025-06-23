<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"

const mapStore = useMapStore()

defineProps({
  hideCloseButton: {
    type: Boolean,
    default: false
  }
})
</script>

<template>
  <div
    v-if="mapStore.contextData.data"
    class="map-context-data-container w-full"
    data-cy="map-context-data"
  >
    <map-context-data-plantability
      v-if="mapStore.selectedDataType === DataType.PLANTABILITY"
      :data="mapStore.contextData.data as PlantabilityData"
      :hide-close-button="hideCloseButton"
      @close="() => mapStore.contextData.removeData()"
    />
    <map-context-data-vulnerability
      v-if="mapStore.selectedDataType === DataType.VULNERABILITY"
      :data="mapStore.contextData.data as VulnerabilityData"
      :hide-close-button="hideCloseButton"
      @close="() => mapStore.contextData.removeData()"
    />
    <map-context-data-climate-zone
      v-if="mapStore.selectedDataType === DataType.CLIMATE_ZONE"
      :data="mapStore.contextData.data as ClimateData"
      :hide-close-button="hideCloseButton"
      @close="() => mapStore.contextData.removeData()"
    />
  </div>
</template>
