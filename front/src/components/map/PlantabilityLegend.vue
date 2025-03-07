<script setup lang="ts">
import ScoreLabel from "./ScoreLabel.vue"
</script>

<template>
  <div
    class="plantability-legend flex items-center justify-center text-xs leading-3 gap-2"
    data-cy="plantability-legend"
  >
    <span class="plantability-legend-text">Non plantable</span>
    <div class="flex p-2">
      <score-label
        v-for="index in [0, 2, 4, 6, 8, 10]"
        :key="index"
        class="flex items-center justify-center"
        :score="index"
        :label="`${index}`"
        size="small"
      />
    </div>
    <span class="plantability-legend-text">Plantable</span>
  </div>
</template>

<style scoped>
.plantability-legend {
  font-family: var(--font-accent);
}

.plantability-legend-text {
  font-size: 0.9rem;
  line-height: 0.75rem;
}
</style>
