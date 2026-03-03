<script lang="ts" setup>
import { computed } from "vue"
import { type VegetationData } from "@/types/vegetation"
import ContextDataMainContainer from "@/components/contextData/shared/ContextDataMainContainer.vue"
import { useMapStore } from "@/stores/map"
import VegestrateContextDataInfo from "./vegestrate/VegestrateContextDataInfo.vue"

const mapStore = useMapStore()
const zoomLevel = computed(() => mapStore.currentZoom)

interface VegetationCardProps {
  data?: VegetationData | null
}

const props = withDefaults(defineProps<VegetationCardProps>(), {
  data: null
})

const currentData = computed<VegetationData | null>(() => props.data ?? null)
</script>

<template>
  <ContextDataMainContainer
    color-scheme="vegetation"
    title="vegetation"
    description="Données de végétation issues de la fusion de la classification du LIDAR 2023 et de la classification des orthophotos à l'aide de FLAIR-HUB de l'IGN."
    :data="currentData"
    empty-message="Cliquez sur un carreau."
    :zoom-level="zoomLevel"
  >
    <template #content="{ data: vegetationData }">
      <VegestrateContextDataInfo :data="vegetationData" />
    </template>
  </ContextDataMainContainer>
</template>
