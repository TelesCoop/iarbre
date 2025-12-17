<script lang="ts" setup>
import { withDefaults, computed } from "vue"
import type { ClimateData } from "@/types/climate"
import ContextDataMainContainer from "@/components/contextData/shared/ContextDataMainContainer.vue"
import ClimateContextDataMetrics from "@/components/contextData/climate/ClimateContextDataMetrics.vue"
import ClimateContextDataScore from "@/components/contextData/climate/ClimateContextDataScore.vue"
import UnsupportedShapeModeMessage from "@/components/contextData/shared/UnsupportedShapeModeMessage.vue"
import { useMapStore } from "@/stores/map"

interface ClimateDataProps {
  data?: ClimateData | null
  hideCloseButton?: boolean
  fullHeight?: boolean
}

const props = withDefaults(defineProps<ClimateDataProps>(), {
  data: null
})

const mapStore = useMapStore()

const primaryData = computed<ClimateData | null>(() => props.data)
</script>

<template>
  <context-data-main-container
    color-scheme="climate"
    title="lcz"
    description="Indicateurs climatiques locaux pour une zone sélectionnée. Ces données incluent des informations sur les bâtiments, les surfaces et la végétation."
    :data="mapStore.isShapeMode ? {} : primaryData"
    :full-height="props.fullHeight"
    :hide-close-button="props.hideCloseButton"
    empty-message="Cliquez sur un carreau"
    :hide-description="mapStore.isShapeMode"
    :hide-empty-message="mapStore.isShapeMode"
  >
    <template #score="{ data: climateData }">
      <unsupported-shape-mode-message />
      <climate-context-data-score v-if="!mapStore.isShapeMode" :data="climateData" />
    </template>
    <template #content="{ data: climateData, fullHeight: isFullHeight }">
      <climate-context-data-metrics
        v-if="!mapStore.isShapeMode"
        :data="climateData"
        :full-height="isFullHeight"
      />
    </template>
  </context-data-main-container>
</template>
