<script lang="ts" setup>
import type { ClimateData } from "@/types/climate"
import MapContextHeader from "@/components/contextData/MapContextHeader.vue"
import ClimateContextDataMetrics from "@/components/contextData/climate/ClimateContextDataMetrics.vue"
import { DataType, DataTypeToLabel } from "@/utils/enum"

interface ClimateDataProps {
  data: ClimateData
  hideCloseButton?: boolean
  fullHeight?: boolean
}

const props = defineProps<ClimateDataProps>()
const emit = defineEmits<{
  close: []
}>()

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
    <div class="map-context-panel-content">
      <climate-context-data-metrics :data="data" :full-height="props.fullHeight" />
    </div>
  </div>
</template>
