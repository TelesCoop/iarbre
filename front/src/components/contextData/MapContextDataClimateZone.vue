<script lang="ts" setup>
import { withDefaults } from "vue"
import type { ClimateData } from "@/types/climate"
import MapContextHeader from "@/components/contextData/MapContextHeader.vue"
import ClimateContextDataMetrics from "@/components/contextData/climate/ClimateContextDataMetrics.vue"
import ClimateContextDataScore from "@/components/contextData/climate/ClimateContextDataScore.vue"
import EmptyMessage from "@/components/EmptyMessage.vue"

interface ClimateDataProps {
  data?: ClimateData | null
  hideCloseButton?: boolean
  fullHeight?: boolean
}

const props = withDefaults(defineProps<ClimateDataProps>(), {
  data: null
})
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
    />
    <div class="map-context-panel-content">
      <div v-if="props.data">
        <climate-context-data-score :data="props.data" />
        <climate-context-data-metrics :data="props.data" :full-height="props.fullHeight" />
      </div>
      <empty-message v-else data-cy="empty-message" message="Cliquez sur un carreau" />
    </div>
  </div>
</template>
