<script lang="ts" setup>
import { withDefaults } from "vue"
import type { ClimateData } from "@/types/climate"
import ContextDataMainContainer from "@/components/contextData/shared/ContextDataMainContainer.vue"
import ClimateContextDataMetrics from "@/components/contextData/climate/ClimateContextDataMetrics.vue"
import ClimateContextDataScore from "@/components/contextData/climate/ClimateContextDataScore.vue"

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
  <context-data-main-container
    color-scheme="climate"
    title="lcz"
    description="Indicateurs climatiques locaux pour une zone sélectionnée. Ces données incluent des informations sur les bâtiments, les surfaces et la végétation."
    :data="props.data"
    :full-height="props.fullHeight"
    :hide-close-button="props.hideCloseButton"
    empty-message="Cliquez sur un carreau"
  >
    <template #score="{ data: climateData }">
      <climate-context-data-score :data="climateData" />
    </template>
    <template #content="{ data: climateData, fullHeight: isFullHeight }">
      <climate-context-data-metrics :data="climateData" :full-height="isFullHeight" />
    </template>
  </context-data-main-container>
</template>
