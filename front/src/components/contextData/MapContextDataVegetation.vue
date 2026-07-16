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
  mapStore.showVegestrateHeight ? { height: mapStore.vegetationHeightAtPoint } : currentData.value
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
      <section v-if="mapStore.showVegestrateHeight" class="flex w-full flex-col gap-3">
        <h3 class="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Hauteur de végétation
        </h3>
        <VegestrateHeightGauge />
      </section>
      <VegestrateContextDataInfo v-else-if="currentData" :data="currentData" />
    </template>
  </ContextDataMainContainer>
</template>
