<script lang="ts" setup>
import PlantabilityScorePopup from "@/components/map/popup/PlantabilityScorePopupContent.vue"
import ClimateZoneScorePopup from "@/components/map/popup/ClimateZoneScorePopupContent.vue"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import { computed } from "vue"
import { copyToClipboard } from "@/utils/clipboard"
import { useToast } from "primevue/usetoast"
import VulnerabilityScorePopup from "@/components/map/popup/VulnerabilityScorePopupContent.vue"

const mapStore = useMapStore()
const toast = useToast()

const popupData = computed(() => mapStore.popupData)
const coords = computed(
  () => `${popupData.value?.lat.toFixed(5)}° N, ${popupData.value?.lng.toFixed(5)}° E`
)

const copy = (text: string) => {
  copyToClipboard(text)
  toast.add({
    severity: "success",
    summary: "Coordonnées copiées",
    life: 3000,
    group: "br"
  })
}
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
