<script lang="ts" setup>
import { withDefaults, computed } from "vue"
import type { ClimateData } from "@/types/climate"
import MapContextHeader from "@/components/contextData/MapContextHeader.vue"
import ClimateContextDataMetrics from "@/components/contextData/climate/ClimateContextDataMetrics.vue"
import EmptyMessage from "@/components/EmptyMessage.vue"
import { CLIMATE_ZONE_COLOR } from "@/utils/climateZone"

interface ClimateDataProps {
  data?: ClimateData | null
  hideCloseButton?: boolean
  fullHeight?: boolean
}

const props = withDefaults(defineProps<ClimateDataProps>(), {
  data: null
})

const zoneBackgroundColor = computed(() =>
  props.data?.lczIndex ? CLIMATE_ZONE_COLOR[props.data.lczIndex] || "#bcbcbc" : "#bcbcbc"
)
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
        <div class="map-context-card text-lg" :style="{ backgroundColor: zoneBackgroundColor }">
          <span class="text-center"
            >Zone climatique locale : <br />
            {{ props.data.lczDescription }}</span
          >
        </div>
        <climate-context-data-metrics :data="props.data" :full-height="props.fullHeight" />
      </div>
      <empty-message v-else data-cy="empty-message" message="Cliquez sur un carreau" />
    </div>
  </div>
</template>
