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
const handleClose = () => {
  emit("close")
}
</script>

<template>
  <div
    aria-describedby="plantability-description"
    aria-labelledby="plantability-title"
    class="max-w-md mx-auto bg-white shadow-lg overflow-hidden rounded-md"
    role="dialog"
  >
    <map-context-header
      description="Calcul basé sur la pondération de +37 paramètres"
      title="Score de plantabilité"
      @close="handleClose"
    />
    <div class="p-2 md:p-4 flex flex-col gap-2 md:gap-4">
      <plantability-context-data-score
        :percentage="scorePercentage"
        :score="data.plantabilityNormalizedIndice"
      />
      <plantability-context-data-list :data="data" />
    </div>
  </div>
</template>
