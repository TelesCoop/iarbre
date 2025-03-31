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

const score = computed(() => Math.round(10 * Number(props.popupData.id)))
const label = computed(() => {
  if (score.value >= 5) return "Plantabilité élevée"
  return "Plantabilité faible"
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
