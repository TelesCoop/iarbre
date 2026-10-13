<script lang="ts" setup>
import { computed } from "vue"
import { type BiosphereIntegrityData } from "@/types/biosphereIntegrity"
import ContextDataMainContainer from "@/components/contextData/shared/ContextDataMainContainer.vue"
import BiosphereLandCoverInfo from "@/components/contextData/biosphereIntegrity/BiosphereLandCoverInfo.vue"
import { useMapStore } from "@/stores/map"
import {
  BIOSPHERE_DETAIL_ZOOM,
  BIOSPHERE_CLASSES,
  BIOSPHERE_DETAIL_CLASSES,
  biosphereColor
} from "@/utils/biosphere_functional_integrity"
import { getContrastTextHex } from "@/utils/color"
import ContextDataScoreHeader from "@/components/contextData/shared/ContextDataScoreHeader.vue"

const mapStore = useMapStore()
const zoomLevel = computed(() => mapStore.currentZoom)

interface BiosphereIntegrityCardProps {
  data?: BiosphereIntegrityData | null
}

const props = defineProps<BiosphereIntegrityCardProps>()

const indiceColor = computed(() =>
  biosphereColor(
    props.data?.indice ?? 0,
    zoomLevel.value >= BIOSPHERE_DETAIL_ZOOM ? BIOSPHERE_DETAIL_CLASSES : BIOSPHERE_CLASSES
  )
)

const indiceValue = computed(() => props.data?.indice ?? 0)

const indiceDisplay = computed(() => `${indiceValue.value}%`)

const indiceTextColor = computed(() => getContrastTextHex(indiceColor.value))
</script>

<template>
  <ContextDataMainContainer
    color-scheme="biosphereIntegrity"
    title="biosphereIntegrity"
    description="Indice Fonctionnel de la Biosphère calculé à partir des bases de données de couverture des sols Cosia (donnée 2023 produite par l'IGN) et CarHab (donnée produite par l'IGN et l'Université Jean Monnet)"
    :data="data"
    empty-message="Cliquez sur une zone."
    :zoom-level="zoomLevel"
  >
    <template #score>
      <div data-cy="biosphere-integrity-score">
        <ContextDataScoreHeader
          :swatch-color="indiceColor"
          :swatch-label="indiceDisplay"
          :swatch-text-color="indiceTextColor"
          eyebrow="Intégrité fonctionnelle"
          title="Espace semi-naturel dans un rayon de 500m"
        />
      </div>
    </template>

    <template #content="{ data: biosphereIntegrityData }">
      <div class="biosphere-content">
        <BiosphereLandCoverInfo :data="biosphereIntegrityData" />
      </div>
    </template>
    <template #legend> </template>
  </ContextDataMainContainer>
</template>

<style scoped>
@reference "@/styles/main.css";

.biosphere-content {
  @apply flex min-h-0 flex-col gap-3;
}
</style>
