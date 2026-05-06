<script lang="ts" setup>
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()

const handleScoreClick = (score: number) => {
  mapStore.toggleAndApplyFilter(score)
}

const scoreIndices = [0, 2, 4, 6, 8, 10]
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
  <div class="flex flex-row lg:flex-col items-center gap-2 font-sans" data-cy="plantability-legend">
    <div class="legend-header">
      <span class="legend-title">Plantabilité</span>
    </div>
    <div class="legend-content">
      <div class="legend-label">
        <span class="legend-axis-indicator">−</span>
        <span class="legend-axis-text text-right">Non plantable</span>
      </div>
      <div class="legend-scale">
        <ScoreLabel
          v-for="(scoreIndex, arrayIndex) in scoreIndices"
          :key="scoreIndex"
          :background-color-class="SCORE_BG_CLASSES[scoreIndex]"
          :class="[
            'transition-transform duration-150 ease-out hover:scale-y-110',
            arrayIndex === 0 ? 'rounded-l' : '',
            arrayIndex === scoreIndices.length - 1 ? 'rounded-r' : '',
            mapStore.isFiltered(scoreIndex) ? 'z-10 relative' : ''
          ]"
          :clickable="true"
          :is-selected="mapStore.isFiltered(scoreIndex)"
          :label="`${scoreIndex}`"
          :score="scoreIndex"
          @click="handleScoreClick"
        />
      </div>
      <div class="legend-label">
        <span class="legend-axis-text text-left">Plantable</span>
        <span class="legend-axis-indicator">+</span>
      </div>
    </div>
  </div>
</template>
