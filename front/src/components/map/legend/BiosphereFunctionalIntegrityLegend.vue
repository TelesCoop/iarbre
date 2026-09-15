<script lang="ts" setup>
import { BiosphereIntegrityLegend } from "@/utils/biosphere_functional_integrity"
import FilterableLegendItem from "@/components/map/legend/FilterableLegendItem.vue"

const entries = Object.entries(BiosphereIntegrityLegend) as [string, string][]
</script>

<template>
  <div
    class="flex flex-col items-center gap-1 lg:gap-2 font-sans"
    data-cy="biosphere-integrity-legend"
  >
    <div class="legend-header">
      <span class="legend-title">Part d'espaces naturels</span>
    </div>
    <div class="legend-content">
      <div class="legend-label">
        <span class="legend-axis-indicator">−</span>
        <span class="legend-axis-text">Artificialisé</span>
      </div>
      <div class="scale-stack">
        <div class="legend-scale">
          <FilterableLegendItem
            v-for="([name, color], index) in entries"
            :key="name"
            :value="name"
            :label="name"
            :class="[
              'biosphere-segment',
              index === 0 ? 'rounded-l-sm' : '',
              index === entries.length - 1 ? 'rounded-r-sm' : ''
            ]"
            :data-biosphere="name"
            :style="{ backgroundColor: color }"
            :title="name"
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

.biosphere-segment {
  @apply cursor-pointer border-0 p-0;
  @apply transition-transform duration-150 hover:scale-y-110;
  width: 0.875rem;
  height: 1.125rem;
}

@media (min-width: 1024px) {
  .biosphere-segment {
    width: 1.25rem;
    height: 1.6875rem;
  }
}

.biosphere-segment.is-selected {
  @apply relative z-10 rounded-sm ring-2 ring-gray-600;
}

.biosphere-segment.is-dimmed {
  @apply opacity-40;
}

.scale-stack {
  @apply flex flex-col gap-0.5;
}

.legend-bounds {
  @apply flex justify-between text-2xs font-medium text-gray-500;
}
</style>
