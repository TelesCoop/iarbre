<script setup lang="ts">
import PlantabilityScorePopup from "@/components/map/popup/PlantabilityScorePopupContent.vue"
import ClimateZoneScorePopup from "@/components/map/popup/ClimateZoneScorePopupContent.vue"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"

const mapStore = useMapStore()
defineProps({
  index: {
    required: true,
    type: String
  },
  lat: {
    required: true,
    type: Number
  },
  lng: {
    required: true,
    type: Number
  }
})
</script>

<template>
  <div class="p-2.5 max-w-xs" data-cy="score-popup">
    <div class="flex justify-between">
      <plantability-score-popup
        v-if="mapStore.selectedDataType === DataType.PLANTABILITY"
        :index="Number(index)"
      />
      <climate-zone-score-popup
        v-else-if="mapStore.selectedDataType === DataType.LOCAL_CLIMATE_ZONES"
        :index="index.toString()"
      />
    </div>
    <div class="text-light-green text-right">{{ lat.toFixed(2) }}° N, {{ lng.toFixed(2) }}° E</div>
  </div>
</template>
