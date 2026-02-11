<script lang="ts" setup>
import { ref } from "vue"
import { getZoneDesc } from "@/utils/climateZone"
import { useMapStore } from "@/stores/map"
import ClimateZoneScoreLabel from "@/components/map/score/ClimateZoneScoreLabel.vue"
import ExpandToggle from "../../toggle/ExpandToggle.vue"

const isExpanded = ref(false)
const mapStore = useMapStore()

const zones = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G"]

const handleZoneClick = (zone: string) => {
  mapStore.toggleAndApplyFilter(zone)
}
</script>

<template>
  <div class="climate-legend" data-cy="climate-zones-legend">
    <div class="legend-header">
      <span class="legend-title">Zone climatique locale</span>
    </div>
    <div class="legend-scale">
      <div v-for="(zone, index) in zones" :key="index" class="flex items-center">
        <ClimateZoneScoreLabel
          :zone="zone"
          size="compact"
          :is-first="index === 0"
          :is-last="index === zones.length - 1"
          @click="handleZoneClick(zone)"
        />
      </div>
    </div>
    <ExpandToggle :is-expanded="isExpanded" @toggle="isExpanded = !isExpanded" />
    <div v-if="isExpanded" class="legend-details">
      <div v-for="(zone, index) in zones" :key="'vertical-' + index" class="legend-detail-item">
        <ClimateZoneScoreLabel :zone="zone" size="detailed" @click="handleZoneClick(zone)" />
        <span class="detail-text">LCZ {{ zone }} : {{ getZoneDesc(zone) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.climate-legend {
  @apply flex flex-col items-center gap-2 font-sans;
}

.legend-header {
  @apply flex items-center justify-center;
}

.legend-title {
  @apply text-xs font-medium text-gray-500 uppercase tracking-wide;
}

.legend-scale {
  @apply flex items-center justify-center p-2 rounded overflow-hidden;
}

.legend-details {
  @apply flex flex-col items-start gap-2 mt-2 pt-2 border-t border-gray-200 w-full;
}

.legend-detail-item {
  @apply flex items-center gap-2;
}

.detail-text {
  @apply text-sm text-gray-800;
}
</style>
