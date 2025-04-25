<script lang="ts" setup>
import ScoreLabel from "../ScoreLabel.vue"
import { ScoreLabelSize } from "@/utils/enum"
</script>

<template>
  <div
    class="font-accent flex items-center justify-center text-xs leading-3 gap-2 text-primary-900"
    data-cy="plantability-legend"
  >
    <span class="text-[0.9rem] leading-3">Non plantable</span>
    <div class="flex p-2">
      <score-label
        v-for="index in [0, 2, 4, 6, 8, 10]"
        :key="index"
        :label="`${index}`"
        :score="index"
        :size="ScoreLabelSize.SMALL"
        class="flex items-center justify-center"
      />
    </div>
    <span class="text-[0.9rem] leading-3">Plantable</span>
  </div>
</template>
