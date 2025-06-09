<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"

const mapStore = useMapStore()
</script>

<template>
  <div v-if="mapStore.contextData.data" class="map-tool-container" data-cy="map-context-data">
    <map-context-data-plantability
      v-if="mapStore.selectedDataType === DataType.PLANTABILITY"
      :data="mapStore.contextData.data as PlantabilityData"
      @close="() => mapStore.contextData.removeData()"
    />
    <map-context-data-vulnerability
      v-if="mapStore.selectedDataType === DataType.VULNERABILITY"
      :data="mapStore.contextData.data as VulnerabilityData"
      @close="() => mapStore.contextData.removeData()"
    />
  </div>
</template>

<style>
@reference "@/styles/main.css";
.context-map-data {
  @apply flex flex-col gap-2 w-full;
}
</style>
