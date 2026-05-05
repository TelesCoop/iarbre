<script lang="ts" setup>
import { computed } from "vue"
import { type BiosphereIntegrityData } from "@/types/biosphereIntegrity"
import ContextDataMainContainer from "@/components/contextData/shared/ContextDataMainContainer.vue"
import BiosphereLandCoverInfo from "@/components/contextData/biosphereIntegrity/BiosphereLandCoverInfo.vue"
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
    <template #content="{ data: biosphereIntegrityData }">
      <div class="flex flex-col gap-3">
        <p class="text-sm text-center font-sans">
          Il y a {{ biosphereIntegrityData.indice }}% d'espace semi-naturel dans un rayon de 500m
          autour de la zone 4x4m sélectionnée.
        </p>
        <BiosphereLandCoverInfo :data="biosphereIntegrityData" />
      </div>
    </template>
    <template #legend> </template>
  </context-data-main-container>
</template>
