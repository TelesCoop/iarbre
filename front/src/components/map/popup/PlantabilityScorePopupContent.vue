<script setup lang="ts">
import ScoreLabel from "@/components/map/ScoreLabel.vue"
import { computed } from "vue"
import { ScoreLabelSize } from "@/utils/enum"
import type { MapScorePopupData } from "@/types"

const props = defineProps({
  popupData: {
    required: true,
    type: Object as () => MapScorePopupData
  }
})

const score = computed(() => {
  if (Number(props.popupData.id) < -3) return 0
  if (Number(props.popupData.id) < -2) return 2
  if (Number(props.popupData.id) < -0.5) return 4
  if (Number(props.popupData.id) < 0.75) return 6
  if (Number(props.popupData.id) < 1.5) return 8
  return 10
})

const score = computed(() => Math.round(10 * Number(props.popupData.id)))

const label = computed(() => {
  if (score.value === 0) return "Plantation impossible"
  if (score.value === 2) return "Plantation très contrainte"
  if (score.value === 4) return "Plantation contrainte"
  if (score.value === 6) return "Plantation neutre"
  if (score.value === 8) return "Plantation favorisée"
  return "Plantation très favorisée"
})
</script>

<template>
  <div data-cy="plantability-score-popup" class="p-2.5 max-w-xs">
    <div class="flex-grow mr-1.25">
      <score-label :score="score" :label="`${score}/10`" :size="ScoreLabelSize.HUGE" />
    </div>
    <div class="flex-grow ml-1.25">
      <h3 class="font-accent text-lg" data-cy="plantability-score-label">{{ label }}</h3>
    </div>
  </div>
</template>
