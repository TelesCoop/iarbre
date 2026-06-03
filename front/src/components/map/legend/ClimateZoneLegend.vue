<script lang="ts" setup>
import { ref } from "vue"
import { getZoneDesc } from "@/utils/climateZone"
import { useMapStore } from "@/stores/map"
import ClimateZoneScoreLabel from "@/components/map/score/ClimateZoneScoreLabel.vue"
import ExpandToggle from "../../toggle/ExpandToggle.vue"

const isExpanded = ref(false)
const mapStore = useMapStore()

const zones = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G"]

// LCZ are split in two families: built types (1-9) and land-cover types (A-G)
const builtZones = zones.filter((zone) => /^\d$/.test(zone))
const naturalZones = zones.filter((zone) => !/^\d$/.test(zone))

const zoneGroups = [
  { label: "Bâti", zones: builtZones },
  { label: "Naturel", zones: naturalZones }
]

const handleZoneClick = (zone: string) => {
  mapStore.toggleAndApplyFilter(zone)
}
</script>

<template>
  <div class="flex flex-col items-center gap-1 lg:gap-2 font-sans" data-cy="climate-zones-legend">
    <div class="legend-header">
      <span class="legend-title">Zone climatique locale</span>
    </div>

    <div class="zone-groups">
      <div v-for="group in zoneGroups" :key="group.label" class="zone-group">
        <span class="zone-group-label">{{ group.label }}</span>
        <div class="legend-scale">
          <ClimateZoneScoreLabel
            v-for="(zone, index) in group.zones"
            :key="zone"
            :is-first="index === 0"
            :is-last="index === group.zones.length - 1"
            :zone="zone"
            size="compact"
            @click="handleZoneClick(zone)"
          />
        </div>
      </div>
    </div>

    <ExpandToggle :is-expanded="isExpanded" @toggle="isExpanded = !isExpanded" />

    <div v-if="isExpanded" class="zone-details">
      <div v-for="zone in zones" :key="`detail-${zone}`" class="zone-detail-row">
        <ClimateZoneScoreLabel :zone="zone" size="detailed" @click="handleZoneClick(zone)" />
        <span class="zone-detail-text">LCZ {{ zone }} : {{ getZoneDesc(zone) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.zone-groups {
  @apply flex flex-col items-center gap-2;
  @apply sm:flex-row sm:items-end sm:gap-3;
}

.zone-group {
  @apply flex flex-col items-center gap-1;
}

.zone-group-label {
  @apply text-2xs font-semibold uppercase tracking-wide text-gray-600 lg:text-xs;
}

.zone-details {
  @apply mt-2 flex w-full flex-col items-start gap-2 border-t border-gray-200 pt-2;
}

.zone-detail-row {
  @apply flex items-center gap-2;
}

.zone-detail-text {
  @apply text-xs text-gray-600 lg:text-sm;
}
</style>
