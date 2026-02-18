<script lang="ts" setup>
import { computed } from "vue"
import { type BiosphereIntegrityData } from "@/types/biosphereIntegrity"
import ContextDataMainContainer from "@/components/contextData/shared/ContextDataMainContainer.vue"
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()
const zoomLevel = computed(() => mapStore.currentZoom)

interface BiosphereIntegrityCardProps {
  data?: BiosphereIntegrityData | null
}

defineProps<BiosphereIntegrityCardProps>()
</script>

<template>
  <context-data-main-container
    color-scheme="biosphereIntegrity"
    title="biosphereIntegrity"
    description="Indice Fonctionnel de la Biosphère calculé à partir des bases de données de couverture des sols Cosia (donnée 20223 produite par l'IGN) et CarHab (donnée produite par l'IGN et l'Université Jean Monnet)"
    :data="data"
    empty-message="Cliquez sur une zone."
    :zoom-level="zoomLevel"
  >
    <template #score="{ data: biosphereIntegrityData }">
      <UnsupportedShapeModeMessage />
      <BiosphereIntegrityMainContextDataScore
        v-if="!mapStore.isShapeMode"
        :data="biosphereIntegrityData"
      />
    </template>
    <template #content>
      <div class="text-sm text-center font-sans">
        <p>L'intégrité fonctionnelle de la biosphère pour cette zone.</p>
      </div>
    </template>
    <template #legend> </template>
  </context-data-main-container>
</template>
