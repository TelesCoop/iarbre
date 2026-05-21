<script lang="ts" setup>
import { computed } from "vue"
import { type PlantabilityData } from "@/types/plantability"
import ContextDataMainContainer from "@/components/contextData/shared/ContextDataMainContainer.vue"
import PlantabilityContextDataScore from "@/components/contextData/plantability/PlantabilityContextDataScore.vue"
import PlantabilityContextDataList from "@/components/contextData/plantability/PlantabilityContextDataList.vue"
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()
const zoomLevel = computed(() => mapStore.currentZoom)

interface PlantabilityCardProps {
  data?: PlantabilityData | null
}

const props = withDefaults(defineProps<PlantabilityCardProps>(), {
  data: null
})

const currentData = computed<PlantabilityData | null>(() => props.data)

const scorePercentage = computed(() =>
  currentData.value?.plantabilityNormalizedIndice !== undefined
    ? currentData.value.plantabilityNormalizedIndice * 10
    : null
)

const isMultipleSelection = computed(
  () => currentData.value?.id?.toString().startsWith("polygon-") || false
)

const tileCount = computed(() => {
  if (!isMultipleSelection.value) return 0
  const id = currentData.value?.id?.toString()
  const count = id?.split("-")[1]
  return count ? parseInt(count) : 0
})
</script>

<template>
  <ContextDataMainContainer
    color-scheme="plantability"
    title="plantability"
    :description="
      isMultipleSelection
        ? `Moyenne de ${tileCount} tuiles dans la zone sélectionnée - Calcul basé sur la pondération de +37 paramètres.`
        : 'Calcul basé sur la pondération de +37 paramètres.'
    "
    :data="currentData"
    empty-message="Zommez et cliquez sur un carreau."
    :zoom-level="zoomLevel"
  >
    <template #score="{ data: plantabilityData }">
      <PlantabilityContextDataScore
        v-if="scorePercentage !== null"
        :percentage="scorePercentage"
        :score="plantabilityData.plantabilityNormalizedIndice"
      />
    </template>
    <template #content="{ data: plantabilityData }">
      <PlantabilityContextDataList :data="plantabilityData" />
    </template>
  </ContextDataMainContainer>
</template>

<style scoped>
@reference "@/styles/main.css";
</style>
