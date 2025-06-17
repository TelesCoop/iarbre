<script lang="ts" setup>
import type { ClimateData } from "@/types/climate"
import MapContextHeader from "@/components/contextData/MapContextHeader.vue"
import ClimateContextDataMetrics from "@/components/contextData/climate/ClimateContextDataMetrics.vue"

interface ClimateDataProps {
  data: ClimateData
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
      title="Indicateurs climatiques"
      description="Indicateurs urbains de caractérisation climatique"
      @close="handleClose"
    />
    <div class="map-context-panel-content">
      <climate-context-data-metrics :data="data" />
    </div>
  </div>
</template>
