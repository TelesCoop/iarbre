<script lang="ts" setup>
import PlantabilityScorePopup from "@/components/map/popup/PlantabilityScorePopupContent.vue"
import ClimateZoneScorePopup from "@/components/map/popup/ClimateZoneScorePopupContent.vue"
import VulnerabilityScorePopup from "@/components/map/popup/VulnerabilityScorePopupContent.vue"
import MixPlantabilityVulnerabilityScorePopup from "@/components/map/popup/MixPlantabilityVulnerabilityScorePopupContent.vue"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import { computed } from "vue"
import { copyToClipboard } from "@/utils/clipboard"
import { useToast } from "primevue/usetoast"

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
      <mix-plantability-vulnerability-score-popup
        v-else-if="mapStore.selectedDataType === DataType.MIX_PLANTABILITY_AND_VULNERABILITY"
        :popup-data="popupData"
      />
    </div>
    <div class="w-full flex flex-col">
      <div class="w-full flex justify-end">
        <button
          class="text-md cursor-pointer flex items-center text-green-500 font-accent"
          data-cy="copy-coords-button"
          @click="copy(coords)"
        >
          {{ coords }}
          <svg
            fill="none"
            height="34"
            viewBox="0 0 32 34"
            width="32"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M19.9315 20.3371V11.6619C19.9315 11.0164 19.3878 10.5 18.7381 10.5H11.1934C10.5436 10.5 10 11.0293 10 11.6619V20.3242C10 20.9697 10.5436 21.4861 11.1934 21.4861H18.7249C19.3878 21.4861 19.9182 20.9568 19.9182 20.3242L19.9315 20.3371ZM11.021 20.3371V11.6619C11.021 11.5715 11.1006 11.494 11.1934 11.494H18.7249C18.7249 11.494 18.8177 11.507 18.8442 11.5457C18.8707 11.5844 18.8972 11.6231 18.8972 11.6619V20.3242C18.8972 20.3242 18.884 20.4146 18.8442 20.4404C18.8044 20.4662 18.7646 20.4921 18.7249 20.4921H11.1934C11.1006 20.4921 11.021 20.4146 11.021 20.3242V20.3371ZM21.9867 13.0045V22.3381C21.9867 22.9836 21.4431 23.5 20.7934 23.5H12.5724C12.2939 23.5 12.0552 23.2805 12.0552 22.9965C12.0552 22.7125 12.2807 22.493 12.5724 22.493H20.7934C20.7934 22.493 20.8862 22.4801 20.9127 22.4414C20.9392 22.4027 20.9657 22.364 20.9657 22.3252V13.0045C20.9657 12.7334 21.1912 12.501 21.4829 12.501C21.7746 12.501 22 12.7205 22 13.0045H21.9867Z"
              fill="#B5B5B5"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>
