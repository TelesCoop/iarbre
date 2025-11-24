<script lang="ts" setup>
import { computed, withDefaults } from "vue"
import { type PlantabilityData } from "@/types/plantability"
import ContextDataMainContainer from "@/components/contextData/shared/ContextDataMainContainer.vue"
import PlantabilityContextDataScore from "@/components/contextData/plantability/PlantabilityContextDataScore.vue"
import PlantabilityContextDataList from "@/components/contextData/plantability/PlantabilityContextDataList.vue"
import ClickPlantabilityDivisionData from "../division/ClickPlantabilityDivisionData.vue"
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()
const zoomLevel = computed(() => mapStore.currentZoom)

interface PlantabilityCardProps {
  data?: PlantabilityData[]
}

const props = withDefaults(defineProps<PlantabilityCardProps>(), {
  data: () => []
})

// Les données sont soit une seule tuile, soit des données pré-agrégées du backend
const currentData = computed<PlantabilityData | null>(() => {
  if (!props.data || props.data.length === 0) return null
  console.log("MapContextDataPlantability - props.data:", props.data)
  console.log("MapContextDataPlantability - props.data[0]:", props.data[0])
  console.log("MapContextDataPlantability - codes:", {
    irisCodes: props.data[0]?.irisCodes,
    cityCodes: props.data[0]?.cityCodes
  })
  return props.data[0]
})

const scorePercentage = computed(() =>
  currentData.value?.plantabilityNormalizedIndice !== undefined
    ? currentData.value.plantabilityNormalizedIndice * 10
    : null
)

// Détecter si c'est une sélection multiple (ID commence par "polygon-")
const isMultipleSelection = computed(
  () => currentData.value?.id?.toString().startsWith("polygon-") || false
)

// Extraire le nombre de tuiles du ID (format: "polygon-123")
const tileCount = computed(() => {
  if (!isMultipleSelection.value) return 0
  const id = currentData.value?.id?.toString()
  const count = id?.split("-")[1]
  return count ? parseInt(count) : 0
})
</script>

<template>
  <context-data-main-container
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
      <plantability-context-data-score
        v-if="scorePercentage !== null"
        :percentage="scorePercentage"
        :score="plantabilityData.plantabilityNormalizedIndice"
      />
    </template>
    <template #content="{ data: plantabilityData }">
      <plantability-context-data-list :data="plantabilityData" />
      <click-plantability-division-data :plantability-data="plantabilityData" />
    </template>
  </context-data-main-container>
</template>
