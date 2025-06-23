<template>
  <div
    class="font-accent flex flex-col items-center justify-center text-xs leading-3 gap-2"
    data-cy="climate-zones-legend"
  >
    <div class="flex p-2 flex-wrap justify-center gap-2">
      <div v-for="(zone, index) in zones" :key="index" class="flex items-center gap-1">
        <ClimateZoneScoreLabel :zone="zone" size="compact" @click="handleZoneClick(zone)" />
      </div>
    </div>
    <template v-if="!isMinify">
      <ExpandToggle :is-expanded="isExpanded" @toggle="isExpanded = !isExpanded" />
      <div v-if="isExpanded" class="flex flex-col items-start mt-2 gap-1">
        <div
          v-for="(zone, index) in zones"
          :key="'vertical-' + index"
          class="flex items-center gap-2"
        >
          <ClimateZoneScoreLabel :zone="zone" size="detailed" @click="handleZoneClick(zone)" />
          <span class="text-[0.9rem]">LCZ {{ zone }} : {{ getZoneDesc(zone) }}</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue"
import { getZoneDesc } from "@/utils/climateZone"
import { useMapStore } from "@/stores/map"
import ClimateZoneScoreLabel from "@/components/map/score/ClimateZoneScoreLabel.vue"
import ExpandToggle from "../../toggle/ExpandToggle.vue"

defineProps<{
  isMinify?: boolean
}>()
const isExpanded = ref(false)
const mapStore = useMapStore()

const zones = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G"]

const handleZoneClick = (zone: string) => {
  mapStore.toggleAndApplyFilter(zone)
}
</script>
