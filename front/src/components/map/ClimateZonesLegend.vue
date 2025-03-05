<script setup lang="ts">
import ScoreLabel from "./ScoreLabel.vue"
</script>

<template>
  <div class="climate-zones-legend" data-cy="climate-zones-legend">
    <div class="is-flex">
      <div
        v-for="(zone, index) in ['A', 'B', 'C', 'D', 'E', 'F']"
        :key="index"
        class="climate-zone-item"
      >
        <div class="zone-color" :style="{ backgroundColor: getZoneColor(zone) }"></div>
        <span class="zone-label">{{ zone }}</span>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
function getZoneColor(zone: string): string {
  const colors: Record<string, string> = {
    A: "#FF5733", // Red-orange
    B: "#FFC300", // Yellow
    C: "#DAF7A6", // Light green
    D: "#2ECC71", // Green
    E: "#3498DB", // Blue
    F: "#9B59B6" // Purple
  }
  return colors[zone] || "#CCCCCC"
}
</script>

<style lang="sass" scoped>
.climate-zones-legend
  font-family: $accent-font
  display: flex
  flex-direction: column
  align-items: center
  justify-content: center
  line-height: 0.75rem // 12px
  font-size: 0.75rem // 12px
  gap: 0.5rem

  .is-flex
    display: flex
    padding: 0.5rem
    flex-wrap: wrap
    justify-content: center
    gap: 0.5rem

  .climate-zone-item
    display: flex
    align-items: center
    gap: 0.25rem

  .zone-color
    width: 1rem
    height: 1rem
    border-radius: 0.25rem

  .zone-label
    font-size: 0.9rem
    line-height: 0.75rem
</style>
