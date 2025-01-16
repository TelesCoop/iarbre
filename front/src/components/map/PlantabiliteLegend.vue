<template>
  <div class="plantabilite-legend">
    <span class="plantabilite-legend-text">Non plantable</span>
    <div class="is-flex">
      <div
        v-for="(color, index) in COLORS"
        :key="index"
        class="plantabilite-legend-square"
        :style="{ 'background-color': color }"
      >
        <span v-if="index === 0">0</span>
        <span v-else-if="Math.floor(COLORS.length / 2) === index" class="has-text-black">5</span>
        <span v-else-if="index === COLORS.length - 1">10</span>
      </div>
    </div>
    <span class="plantabilite-legend-text">Plantable</span>
  </div>
</template>

<script lang="ts" setup>
import { COLORS } from "@/utils/colors"
</script>

<style lang="sass" scoped>
.plantabilite-legend
  display: flex
  align-items: center
  justify-content: center
  line-height: 0.75rem // 12px
  font-size: 0.75rem // 12px
  gap: 8px

  .is-flex
    display: flex
    padding: 0.5rem

  .plantabilite-legend-square
    display: flex
    align-items: center
    justify-content: center
    width: 25px
    height: 20px
    color: white
    font-weight: 700

  .plantabilite-legend-text
    font-size: 0.75rem
    line-height: 0.75rem
    font-weight: 600
</style>
