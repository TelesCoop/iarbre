<script setup lang="ts">
import ScoreLabel from "./ScoreLabel.vue"
</script>

<template>
  <div class="plantability-legend" data-cy="plantability-legend">
    <span class="plantability-legend-text">Non plantable</span>
    <div class="is-flex">
      <score-label
        v-for="index in [0, 2, 4, 6, 8, 10]"
        :key="index"
        class="plantability-legend-scale"
        :score="index"
        :label="`${index}`"
        size="small"
      />
    </div>
    <span class="plantability-legend-text">Plantable</span>
  </div>
</template>

<style lang="sass" scoped>
.plantability-legend
  font-family: $accent-font
  display: flex
  align-items: center
  justify-content: center
  line-height: 0.75rem // 12px
  font-size: 0.75rem // 12px
  gap: 8px

  .is-flex
    display: flex
    padding: 0.5rem

  .plantability-legend-scale
    display: flex
    align-items: center
    justify-content: center

  .plantability-legend-text
    font-size: 0.9rem
    line-height: 0.75rem
</style>
