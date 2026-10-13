<script lang="ts" setup>
import { BiosphereIntegrityLegend } from "@/utils/biosphere_functional_integrity"
import ScoreLabel from "@/components/map/score/ScoreLabel.vue"
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()
const entries = Object.entries(BiosphereIntegrityLegend) as [string, string][]
</script>

<template>
  <div
    class="flex flex-col items-center gap-1 lg:gap-2 font-sans"
    data-cy="biosphere-integrity-legend"
  >
    <div class="legend-header">
      <span class="legend-title">Intégrité fonctionnelle de la biosphère</span>
    </div>
    <div class="legend-content pb-3">
      <div class="legend-label">
        <span class="legend-axis-indicator">-</span>
        <span class="legend-axis-text">Artificialisé</span>
      </div>
      <div class="scale-stack">
        <div class="legend-scale">
          <ScoreLabel
            v-for="([name, color], index) in entries"
            :key="name"
            :background-color="color"
            :class="[
              'transition-transform duration-150 ease-out hover:scale-y-110',
              index === 0 ? 'rounded-l' : '',
              index === entries.length - 1 ? 'rounded-r' : '',
              mapStore.isFiltered(name) ? 'z-10 relative' : ''
            ]"
            :clickable="true"
            :data-biosphere="name"
            :is-selected="mapStore.isFiltered(name)"
            :label="name"
            :score="name"
            @click="mapStore.toggleAndApplyFilter(name)"
          />
        </div>
        <div class="legend-bounds">
          <span>0 %</span>
          <span>100 %</span>
        </div>
      </div>
      <div class="legend-label">
        <span class="legend-axis-text">Naturel</span>
        <span class="legend-axis-indicator">+</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.scale-stack {
  @apply relative;
}

.legend-bounds {
  @apply absolute inset-x-0 top-full mt-0.5 flex justify-between text-2xs font-medium text-gray-500;
}
</style>
