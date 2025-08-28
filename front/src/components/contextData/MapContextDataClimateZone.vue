<script lang="ts" setup>
import type { ClimateData } from "@/types/climate"
import MapContextHeader from "@/components/contextData/MapContextHeader.vue"
import ClimateContextDataMetrics from "@/components/contextData/climate/ClimateContextDataMetrics.vue"
import ClimateContextDataScore from "./climate/ClimateContextDataScore.vue"
import { DataType, DataTypeToLabel } from "@/utils/enum"
import { useMapStore } from "@/stores/map"
import { computed } from "vue"

interface ClimateDataProps {
  data: ClimateData
  hideCloseButton?: boolean
  fullHeight?: boolean
}

const props = defineProps<ClimateDataProps>()
const emit = defineEmits<{
  close: []
}>()

const mapStore = useMapStore()
const popupData = computed(() => mapStore.popupData)

const handleClose = () => {
  emit("close")
}
</script>

<template>
  <div
    aria-describedby="climate-description"
    aria-labelledby="climate-title"
    class="map-context-panel"
    role="dialog"
  >
    <map-context-header
      description="Indicateurs climatiques locaux pour une zone sélectionnée. Ces données incluent des informations sur les bâtiments, les surfaces et la végétation."
      :title="DataTypeToLabel[DataType.CLIMATE_ZONE]"
      :hide-close-button="props.hideCloseButton"
      @close="handleClose"
    />
    <climate-context-data-score v-if="popupData" :popup-data="popupData" />
    <empty-message v-else data-cy="empty-message" message="Cliquez sur un zone" />
    <div class="map-context-panel-content">
      <climate-context-data-metrics :data="data" :full-height="props.fullHeight" />
    </div>
  </div>
</template>
