<script setup lang="ts">
import ScoreLabel from "../ScoreLabel.vue"
</script>

<template>
  <div
    class="font-accent flex flex-col items-center justify-center text-xs leading-3 gap-2"
    data-cy="climate-zones-legend"
  >
    <div class="flex p-2 flex-wrap justify-center gap-2">
      <div
        v-for="(zone, index) in ['A', 'B', 'C', 'D', 'E', 'F']"
        :key="index"
        class="flex items-center gap-1"
      >
        <div class="w-4 h-4 rounded" :style="{ backgroundColor: getZoneColor(zone) }"></div>
        <span class="text-[0.9rem] leading-3">{{ zone }}</span>
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
