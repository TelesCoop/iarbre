<script lang="ts" setup>
import { computed } from "vue"
import type { VegetationData } from "@/types/vegetation"
import { getStrateShort, STRATE_CATEGORIES, STRATE_GRADIENT_CSS } from "@/utils/vegetation"
import VegestratePanel from "@/components/contextData/vegestrate/VegestratePanel.vue"

interface VegetationContextDataInfoProps {
  data: VegetationData
}

const props = defineProps<VegetationContextDataInfoProps>()

const dominantStrate = computed(() => getStrateShort(props.data.indice))

const formattedSurface = computed(() =>
  props.data.surface.toLocaleString("fr-FR", { maximumFractionDigits: 2 })
)
</script>

<template>
  <VegestratePanel
    class="strate-info"
    summary-label="Strate dominante"
    aside-note="Classification par hauteur"
    bar-aria-label="Échelle des strates végétales, de la strate herbacée à la strate arborée"
    :bar-background="STRATE_GRADIENT_CSS"
    :categories="STRATE_CATEGORIES"
    filterable
  >
    <template #value>
      <span class="text-3xl font-bold leading-none text-primary-800">{{ dominantStrate }}</span>
      <span class="mt-1 text-sm text-gray-500">Surface : {{ formattedSurface }} m²</span>
    </template>
  </VegestratePanel>
</template>
