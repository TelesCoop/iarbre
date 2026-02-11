<script lang="ts" setup>
import { computed, ref, withDefaults } from "vue"
import { type PlantabilityData } from "@/types/plantability"
import ContextDataMainContainer from "@/components/contextData/shared/ContextDataMainContainer.vue"
import PlantabilityContextDataScore from "@/components/contextData/plantability/PlantabilityContextDataScore.vue"
import PlantabilityContextDataList from "@/components/contextData/plantability/PlantabilityContextDataList.vue"
import ClickPlantabilityDivisionData from "../division/ClickPlantabilityDivisionData.vue"
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

const activeTab = ref<"details" | "divisions">("details")
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
      <!-- Tabs -->
      <div class="tabs-container">
        <button
          :class="['tab-button', { active: activeTab === 'details' }]"
          @click="activeTab = 'details'"
        >
          Détails
        </button>
        <button
          :class="['tab-button', { active: activeTab === 'divisions' }]"
          @click="activeTab = 'divisions'"
        >
          Échelons supérieurs
        </button>
      </div>

      <!-- Tab content -->
      <div class="tab-content">
        <PlantabilityContextDataList v-if="activeTab === 'details'" :data="plantabilityData" />
        <ClickPlantabilityDivisionData
          v-else-if="activeTab === 'divisions'"
          :plantability-data="plantabilityData"
        />
      </div>
    </template>
  </ContextDataMainContainer>
</template>

<style scoped>
@reference "@/styles/main.css";

.tabs-container {
  @apply flex gap-1 mb-4 p-1 bg-gray-100 rounded-lg;
}

.tab-button {
  @apply flex-1 py-2 px-3 text-sm font-medium rounded-md bg-transparent transition-all duration-200 cursor-pointer border-none text-gray-600 hover:text-gray-900;
}

.tab-button.active {
  @apply bg-white text-primary-600;
}

.tab-content {
  @apply flex-1 min-h-0 overflow-y-auto;
}
</style>
