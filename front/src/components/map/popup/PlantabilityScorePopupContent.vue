<script lang="ts" setup>
import PlantabilityContextDataScore from "@/components/contextData/plantability/PlantabilityContextDataScore.vue"
import { computed } from "vue"
import { getPlantabilityScore } from "@/utils/plantability"
import type { MapScorePopupData } from "@/types/map"
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()

const props = defineProps({
  popupData: {
    required: true,
    type: Object as () => MapScorePopupData
  }
})

const score = computed(() => Number(props.popupData.score))
const percentage = computed(() => score.value * 10)
const label = computed(() => getPlantabilityScore(score.value))
// https://github.com/TelesCoop/iarbre/blob/dev/back/api/constants.py#L5
const showDetails = computed(() => mapStore.currentZoom > 16)
</script>

<template>
  <div data-cy="plantability-score-popup">
    <div class="flex items-center gap-3 w-11/12 mb-2">
      <plantability-context-data-score :score="score" :percentage="percentage" />
      <h3 class="font-accent text-sm" data-cy="plantability-score-label">{{ label }}</h3>
    </div>
    <div class="flex w-full items-center justify-center">
      <show-hide-score-button
        v-if="showDetails"
        :feature-id="popupData.id"
        data-cy="toggle-plantability-score-details"
      />
      <p v-else class="text-sm font-sans text-center">
        Zoomez davantage pour consulter le détail de l'occupation des sols.
      </p>
    </div>
    <div class="flex-grow ml-1.25"></div>
  </div>
</template>
