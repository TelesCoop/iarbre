<script lang="ts" setup>
import { computed } from "vue"
import { type BiosphereIntegrityData } from "@/types/biosphereIntegrity"
import ContextDataMainContainer from "@/components/contextData/shared/ContextDataMainContainer.vue"
import BiosphereLandCoverInfo from "@/components/contextData/biosphereIntegrity/BiosphereLandCoverInfo.vue"
import { useMapStore } from "@/stores/map"
import { BIOSPHERE_FUNCTIONAL_INTEGRITY_COLOR_MAP } from "@/utils/biosphere_functional_integrity"

const mapStore = useMapStore()
const zoomLevel = computed(() => mapStore.currentZoom)

interface BiosphereIntegrityCardProps {
  data?: BiosphereIntegrityData | null
}

const props = defineProps<BiosphereIntegrityCardProps>()

const indiceColor = computed(() => {
  const indice = props.data?.indice ?? 0
  const map = BIOSPHERE_FUNCTIONAL_INTEGRITY_COLOR_MAP
  let color = String(map[0])
  for (let i = 1; i < map.length - 1; i += 2) {
    if (indice >= (map[i] as number)) color = String(map[i + 1])
  }
  return color
})
</script>

<template>
  <context-data-main-container
    color-scheme="biosphereIntegrity"
    title="biosphereIntegrity"
    description="Indice Fonctionnel de la Biosphère calculé à partir des bases de données de couverture des sols Cosia (donnée 2023 produite par l'IGN) et CarHab (donnée produite par l'IGN et l'Université Jean Monnet)"
    :data="data"
    empty-message="Cliquez sur une zone."
    :zoom-level="zoomLevel"
  >
    <template #content="{ data: biosphereIntegrityData }">
      <div class="flex flex-col gap-3">
        <div
          class="rounded-lg p-3 text-center border"
          :style="{ backgroundColor: indiceColor + '20', borderColor: indiceColor + '50' }"
        >
          <span class="text-3xl font-bold" :style="{ color: indiceColor }">
            {{ biosphereIntegrityData.indice }}%
          </span>
          <p class="text-xs text-gray-500 mt-1">d'espace semi-naturel dans un rayon de 500m</p>
        </div>
        <BiosphereLandCoverInfo :data="biosphereIntegrityData" />
      </div>
    </template>
    <template #legend> </template>
  </context-data-main-container>
</template>
