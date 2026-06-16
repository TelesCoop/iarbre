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

const heightDisplayData = computed(() =>
  mapStore.vegetationHeightAtPoint !== undefined
    ? { height: mapStore.vegetationHeightAtPoint }
    : null
)

const displayData = computed(() =>
  mapStore.showVegestrateHeight ? heightDisplayData.value : currentData.value
)

const emptyMessage = computed(() =>
  mapStore.showVegestrateHeight ? "Cliquez sur un pixel." : "Cliquez sur un carreau."
)
</script>

<template>
  <ContextDataMainContainer
    color-scheme="vegetation"
    title="vegetation"
    description="Données de végétation issues de la fusion de la classification du LIDAR 2023 et de la classification des orthophotos à l'aide de FLAIR-HUB de l'IGN."
    :data="displayData"
    :empty-message="emptyMessage"
    :zoom-level="zoomLevel"
  >
    <template #content>
      <div v-if="mapStore.showVegestrateHeight" class="height-info">
        <span class="height-value">
          {{
            heightDisplayData?.height !== null && heightDisplayData?.height !== undefined
              ? `${heightDisplayData.height} m`
              : "Hors zone de végétation"
          }}
        </span>
      </div>
      <VegestrateContextDataInfo v-else-if="currentData" :data="currentData" />
    </template>
  </ContextDataMainContainer>
</template>

<style scoped>
@reference "@/styles/main.css";

.height-info {
  @apply flex items-center justify-center p-4;
}

.height-value {
  @apply text-2xl font-bold text-gray-800;
}
</style>
