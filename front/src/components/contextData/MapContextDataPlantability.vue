<script lang="ts" setup>
import { computed } from "vue"
import { type PlantabilityData } from "@/types/plantability"
import MapContextHeader from "@/components/contextData/MapContextHeader.vue"
import PlantabilityContextDataScore from "@/components/contextData/plantability/PlantabilityContextDataScore.vue"
import PlantabilityContextDataList from "@/components/contextData/plantability/PlantabilityContextDataList.vue"

interface PlantabilityCardProps {
  data: PlantabilityData
}

const props = defineProps<PlantabilityCardProps>()
const emit = defineEmits<{
  close: []
}>()

const scorePercentage = computed(() => props.data?.plantabilityNormalizedIndice * 10)
</script>

<template>
  <div
    aria-describedby="plantability-description"
    aria-labelledby="plantability-title"
    class="map-context-panel"
    role="dialog"
  >
    <map-context-header
      description="Calcul basé sur la pondération de +37 paramètres"
      title="Score de plantabilité"
      @close="emit('close')"
    />
    <div class="map-context-panel-content">
      <plantability-context-data-score
        :percentage="scorePercentage"
        :score="data.plantabilityNormalizedIndice"
      />
      <plantability-context-data-list :data="data" />
    </div>
  </div>
</template>
