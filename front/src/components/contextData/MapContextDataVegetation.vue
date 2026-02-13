<script lang="ts" setup>
import { computed } from "vue"
import { type VegetationData } from "@/types/vegetation"
import ContextDataMainContainer from "@/components/contextData/shared/ContextDataMainContainer.vue"
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()
const zoomLevel = computed(() => mapStore.currentZoom)

interface VegetationCardProps {
  data?: VegetationData | null
}

defineProps<VegetationCardProps>()
</script>

<template>
  <context-data-main-container
    color-scheme="vegetation"
    title="vegetation"
    description="Données de végétation issues de la fusion de la classification du LIDAR 2023 et de la classification des orthophotos à l'aide de FLAIR-HUB de l'IGN."
    :data="data"
    hide-empty-message
    :zoom-level="zoomLevel"
  >
    <template #content>
      <div class="text-sm text-center font-sans">
        <p>Données de végétation disponibles pour cette zone.</p>
      </div>
    </template>
  </context-data-main-container>
</template>
