<script setup lang="ts">
import ScoreLabel from "@/components/map/ScoreLabel.vue"
import { computed } from "vue"
import { ScoreLabelSize } from "@/utils/enum"

const props = defineProps({
  index: {
    required: true,
    type: Number
  }
})

const score = computed(() => {
  if (props.index < -3) return 0
  if (props.index < -2) return 2
  if (props.index < -0.5) return 4
  if (props.index < 0.75) return 6
  if (props.index < 1.5) return 8
  return 10
})

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
