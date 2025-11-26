<script lang="ts" setup>
import { withDefaults, computed } from "vue"
import type { ClimateData } from "@/types/climate"
import ContextDataMainContainer from "@/components/contextData/shared/ContextDataMainContainer.vue"
import ClimateContextDataMetrics from "@/components/contextData/climate/ClimateContextDataMetrics.vue"
import ClimateContextDataScore from "@/components/contextData/climate/ClimateContextDataScore.vue"
import UnsupportedShapeModeMessage from "@/components/contextData/shared/UnsupportedShapeModeMessage.vue"
import { useMapStore } from "@/stores/map"

interface ClimateDataProps {
  data?: ClimateData[]
  hideCloseButton?: boolean
  fullHeight?: boolean
}

const props = withDefaults(defineProps<ClimateDataProps>(), {
  data: () => []
})

const mapStore = useMapStore()

// Pour les zones climatiques, on affiche la première zone ou null
const primaryData = computed<ClimateData | null>(() => {
  if (!props.data || props.data.length === 0) return null
  return props.data[0]
})

const tileCount = computed(() => props.data?.length || 0)
</script>

<template>
  <context-data-main-container
    color-scheme="climate"
    title="lcz"
    :description="
      tileCount > 1
        ? `${tileCount} zones sélectionnées - Indicateurs climatiques locaux. Ces données incluent des informations sur les bâtiments, les surfaces et la végétation.`
        : 'Indicateurs climatiques locaux pour une zone sélectionnée. Ces données incluent des informations sur les bâtiments, les surfaces et la végétation.'
    "
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
