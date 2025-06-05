<script lang="ts" setup>
import ScoreLabel from "@/components/map/ScoreLabel.vue"
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
const label = computed(() => getPlantabilityScore(score.value))
const toggleTileDetails = () => {
  if (!mapStore.tileDetails) {
    mapStore.setTileDetails(props.popupData.id)
  } else {
    mapStore.removeTileDetails()
  }
}
</script>

<template>
  <div data-cy="plantability-score-popup">
    <div class="flex items-center gap-3 w-11/12 mb-2">
      <score-label :label="`${score}/10`" :score="score" is-selected />
      <h3 class="font-accent text-sm" data-cy="plantability-score-label">{{ label }}</h3>
    </div>
    <div class="flex w-full items-center justify-center">
      <Button
        :label="mapStore.tileDetails ? 'Masquer les détails' : 'Voir les détails'"
        class="font-accent"
        data-cy="toggle-plantability-score-details"
        severity="secondary"
        size="small"
        @click="toggleTileDetails"
      />
    </div>
    <div class="flex-grow ml-1.25"></div>
  </div>
</template>
