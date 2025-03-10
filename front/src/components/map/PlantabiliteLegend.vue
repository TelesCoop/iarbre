<script setup lang="ts">
import ScoreLabel from "./ScoreLabel.vue"
</script>

<template>
  <div class="plantabilite-legend flex items-center justify-center text-xs leading-3 gap-2">
    <span class="plantabilite-legend-text">Non plantable</span>
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
    <span class="plantabilite-legend-text">Plantable</span>
  </div>
</template>

<style scoped>
.plantabilite-legend {
  font-family: var(--font-accent);
}

.plantabilite-legend-text {
  font-size: 0.9rem;
  line-height: 0.75rem;
}
</style>
