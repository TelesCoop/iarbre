<script lang="ts" setup>
import ScoreLabel from "@/components/map/ScoreLabel.vue"
import { computed } from "vue"
import { ScoreLabelSize } from "@/utils/enum"
import { getPlantabilityScore } from "@/utils/plantability"
import type { MapScorePopupData } from "@/types"

const props = defineProps({
  popupData: {
    required: true,
    type: Object as () => MapScorePopupData
  }
})

const score = computed(() => Number(props.popupData.id))
const label = computed(() => getPlantabilityScore(Number(props.popupData.id)))
</script>

<template>
  <div data-cy="plantability-score-popup">
    <div class="flex items-center gap-3 mr-1.25 w-11/12">
      <score-label :label="`${score}/10`" :score="score" :size="ScoreLabelSize.HUGE" />
      <h3 class="font-accent text-lg" data-cy="plantability-score-label">{{ label }}</h3>
    </div>
    <div class="flex-grow ml-1.25"></div>
  </div>
</template>
