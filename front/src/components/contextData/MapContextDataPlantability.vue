<script lang="ts" setup>
import { computed, withDefaults } from "vue"
import { type PlantabilityData } from "@/types/plantability"
import ContextDataMainContainer from "@/components/contextData/shared/ContextDataMainContainer.vue"
import PlantabilityContextDataScore from "@/components/contextData/plantability/PlantabilityContextDataScore.vue"
import PlantabilityContextDataList from "@/components/contextData/plantability/PlantabilityContextDataList.vue"

interface PlantabilityCardProps {
  data?: PlantabilityData | null
}

const props = withDefaults(defineProps<PlantabilityCardProps>(), {
  data: null
})

const scorePercentage = computed(() =>
  props.data?.plantabilityNormalizedIndice !== undefined
    ? props.data.plantabilityNormalizedIndice * 10
    : null
)
</script>

<template>
  <context-data-main-container
    color-scheme="plantability"
    title="plantability"
    description="Calcul basé sur la pondération de +37 paramètres"
    :data="props.data"
    empty-message="Zommez et cliquez sur un carreau"
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
    </template>
  </context-data-main-container>
</template>
