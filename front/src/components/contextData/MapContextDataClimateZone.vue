<script lang="ts" setup>
import type { ClimateData } from "@/types/climate"
import MapContextHeader from "@/components/contextData/MapContextHeader.vue"
import ClimateContextDataMetrics from "@/components/contextData/climate/ClimateContextDataMetrics.vue"

interface ClimateDataProps {
  data: ClimateData
}

defineProps<ClimateDataProps>()
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
      title="Zones climatiques locales"
      @close="handleClose"
    />
    <div class="map-context-panel-content">
      <climate-context-data-metrics :data="data" />
    </div>
  </div>
</template>
