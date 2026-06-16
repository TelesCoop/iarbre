<script lang="ts" setup>
import { computed } from "vue"
import { type VegetationData } from "@/types/vegetation"
import ContextDataMainContainer from "@/components/contextData/shared/ContextDataMainContainer.vue"
import { useMapStore } from "@/stores/map"
import VegestrateContextDataInfo from "./vegestrate/VegestrateContextDataInfo.vue"
import VegestrateHeightGauge from "./vegestrate/VegestrateHeightGauge.vue"

const mapStore = useMapStore()
const zoomLevel = computed(() => mapStore.currentZoom)

interface VegetationCardProps {
  data?: VegetationData | null
}

const props = withDefaults(defineProps<VegetationCardProps>(), {
  data: null
})

const currentData = computed<VegetationData | null>(() => props.data ?? null)

const displayData = computed(() =>
  mapStore.showVegestrateHeight
    ? mapStore.vegetationHeightAtPoint !== undefined
      ? { height: mapStore.vegetationHeightAtPoint }
      : null
    : currentData.value
)

const emptyMessage = computed(() =>
  mapStore.showVegestrateHeight ? "Cliquez sur un pixel." : "Cliquez sur un carreau."
)
</script>

<template>
  <ContextDataMainContainer
    color-scheme="vegetation"
    title="Végétation"
    description="Données de végétation issues de la fusion de la classification du LIDAR 2023 et de la classification des orthophotos à l'aide de FLAIR-HUB de l'IGN."
    :data="displayData"
    :empty-message="emptyMessage"
    :zoom-level="zoomLevel"
  >
    <template #content>
      <VegestrateHeightGauge v-if="mapStore.showVegestrateHeight" />
      <VegestrateContextDataInfo v-else-if="currentData" :data="currentData" />
    </template>
  </ContextDataMainContainer>
</template>
