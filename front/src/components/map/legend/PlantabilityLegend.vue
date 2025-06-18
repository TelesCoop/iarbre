<script lang="ts" setup>
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()

const handleScoreClick = (score: number) => {
  mapStore.toggleAndApplyFilter(score)
}
const SCORE_BG_CLASSES: Record<number, string> = {
  0: "bg-scale-0",
  1: "bg-scale-1",
  2: "bg-scale-2",
  3: "bg-scale-3",
  4: "bg-scale-4",
  5: "bg-scale-5",
  6: "bg-scale-6",
  7: "bg-scale-7",
  8: "bg-scale-8",
  9: "bg-scale-9",
  10: "bg-scale-10"
}
</script>

<template>
  <div
    class="font-accent flex items-center justify-center text-xs leading-3 gap-2"
    data-cy="plantability-legend"
  >
    <div class="flex items-center flex-wrap justify-center gap-2 lg:gap-[7px] px-2">
      <span class="text-xs lg:text-sm leading-3">Non plantable</span>
      <score-label
        v-for="index in [0, 2, 4, 6, 8, 10]"
        :key="index"
        :clickable="true"
        :is-selected="mapStore.isFiltered(index)"
        :label="`${index}`"
        :score="index"
        class="flex items-center justify-center"
        :background-color-class="SCORE_BG_CLASSES[index]"
        @click="handleScoreClick"
      />
    </div>
    <span class="text-xs lg:text-sm leading-3">Plantable</span>
  </div>
</template>
