<script lang="ts" setup>
import PlantabilityScorePopup from "@/components/map/popup/PlantabilityScorePopupContent.vue"
import ClimateZoneScorePopup from "@/components/map/popup/ClimateZoneScorePopupContent.vue"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import { computed } from "vue"
import VulnerabilityScorePopup from "@/components/map/popup/VulnerabilityScorePopupContent.vue"

const mapStore = useMapStore()

const popupData = computed(() => mapStore.popupData)
</script>

<template>
  <div v-if="popupData" class="max-w-xs" data-cy="score-popup">
    <div class="flex justify-between">
      <plantability-score-popup
        v-if="mapStore.selectedDataType === DataType.PLANTABILITY"
        :popup-data="popupData"
      />
      <climate-zone-score-popup
        v-else-if="mapStore.selectedDataType === DataType.CLIMATE_ZONE"
        :popup-data="popupData"
      />
      <vulnerability-score-popup
        v-else-if="mapStore.selectedDataType === DataType.VULNERABILITY"
        :popup-data="popupData"
      />
    </div>
  </div>
</template>
