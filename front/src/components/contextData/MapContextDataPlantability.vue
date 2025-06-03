<script lang="ts" setup>
import { computed } from "vue"
import { type PlantabilityTile } from "@/types/plantability"
import PlantabilityContextDataHeader from "@/components/contextData/plantability/PlantabilityContextDataHeader.vue"
import PlantabilityContextDataScore from "@/components/contextData/plantability/PlantabilityContextDataScore.vue"
import PlantabilityContextDataList from "@/components/contextData/plantability/PlantabilityContextDataList.vue"
interface PlantabilityCardProps {
  data: PlantabilityTile
}

const props = defineProps<PlantabilityCardProps>()
const emit = defineEmits<{
  close: []
}>()

const scorePercentage = computed(() => (props.data.plantabilityNormalizedIndice / 10) * 100)

const handleClose = () => {
  emit("close")
}
</script>

<template>
  <div
    class="plantability-card max-w-md mx-auto bg-white shadow-lg overflow-hidden rounded-lg"
    role="dialog"
    aria-labelledby="plantability-title"
    aria-describedby="plantability-description"
  >
    <plantability-context-data-header @close="handleClose" />
    <main class="p-4 flex flex-col gap-6">
      <plantability-context-data-score
        :score="data.plantabilityNormalizedIndice"
        :percentage="scorePercentage"
      />

      <plantability-context-data-list :data="data" />
    </main>
  </div>
</template>
