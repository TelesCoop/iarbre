<script lang="ts" setup>
import PlantabilityContextDataScore from "@/components/contextData/plantability/PlantabilityContextDataScore.vue"
import { computed, ref, onMounted } from "vue"
import { getPlantabilityScore } from "@/utils/plantability"
import type { MapScorePopupData } from "@/types/map"
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()
const currentZoom = ref(14)

const props = defineProps({
  popupData: {
    required: true,
    type: Object as () => MapScorePopupData
  }
})

const score = computed(() => Number(props.popupData.score))
const percentage = computed(() => score.value * 10)
const label = computed(() => getPlantabilityScore(score.value))
const showDetails = computed(() => currentZoom.value > 16)

const updateZoom = () => {
  const mapInstance = mapStore.getMapInstance("default")
  if (mapInstance) {
    currentZoom.value = mapInstance.getZoom()
  }
}

onMounted(() => {
  const mapInstance = mapStore.getMapInstance("default")
  if (mapInstance) {
    currentZoom.value = mapInstance.getZoom()
    mapInstance.on("zoomend", updateZoom)
  }
})
</script>

<template>
  <div data-cy="plantability-score-popup">
    <div class="flex items-center gap-3 w-11/12 mb-2">
      <plantability-context-data-score :score="score" :percentage="percentage" />
      <h3 class="font-accent text-sm" data-cy="plantability-score-label">{{ label }}</h3>
    </div>
    <div class="flex w-full items-center justify-center">
      <Button
        v-if="showDetails"
        :label="mapStore.contextData.data ? 'Masquer les détails' : 'Voir les détails'"
        class="font-accent"
        data-cy="toggle-plantability-score-details"
        severity="secondary"
        size="small"
        @click="mapStore.contextData.toggleContextData(props.popupData.id)"
      />
      <p v-else class="text-sm font-sans text-center">
        Zoomez davantage pour consulter le détail de l'occupation des sols.
      </p>
    </div>
    <div class="flex-grow ml-1.25"></div>
  </div>
</template>
