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
  <div class="plantability-legend" data-cy="plantability-legend">
    <div class="legend-header">
      <span class="legend-title">Plantabilité</span>
    </div>
    <div class="legend-content">
      <div class="legend-label legend-label-left">
        <span class="label-indicator">−</span>
        <span class="label-text">Non plantable</span>
      </div>
      <div class="legend-scale">
        <ScoreLabel
          v-for="(scoreIndex, arrayIndex) in scoreIndices"
          :key="scoreIndex"
          :background-color-class="SCORE_BG_CLASSES[scoreIndex]"
          :class="[
            'score-item',
            arrayIndex === 0 ? 'rounded-l' : '',
            arrayIndex === scoreIndices.length - 1 ? 'rounded-r' : '',
            mapStore.isFiltered(scoreIndex) ? 'is-filtered' : ''
          ]"
          :clickable="true"
          :is-selected="mapStore.isFiltered(scoreIndex)"
          :label="`${scoreIndex}`"
          :score="scoreIndex"
          @click="handleScoreClick"
        />
      </div>
      <div class="legend-label legend-label-right">
        <span class="label-text">Plantable</span>
        <span class="label-indicator">+</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.plantability-legend {
  @apply flex flex-col gap-2 font-sans;
}

.legend-header {
  @apply flex items-center justify-center;
}

.legend-title {
  @apply text-xs font-medium text-gray-500 uppercase tracking-wide;
}

.legend-content {
  @apply flex items-center justify-center gap-3;
}

.legend-label {
  @apply hidden lg:flex items-center gap-1 text-xs text-gray-600;
}

.label-indicator {
  @apply font-bold text-sm text-gray-400;
}

.label-text {
  @apply font-serif text-sm leading-tight;
}

.legend-label-left .label-text {
  @apply text-right;
}

.legend-label-right .label-text {
  @apply text-left;
}

.legend-scale {
  @apply flex items-center rounded overflow-hidden;
}

.score-item {
  @apply transition-transform duration-150 ease-out hover:scale-y-110;
}

.score-item.is-filtered {
  @apply z-10 relative;
}
</style>
