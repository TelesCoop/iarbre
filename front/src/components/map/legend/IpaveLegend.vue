<template>
  <div
    class="font-accent flex flex-col items-center justify-center text-xs leading-3 gap-2"
    data-cy="climate-zones-legend"
  >
    <div class="p-2 justify-center">
      <div
        v-for="(zone, index) in zones"
        :key="'vertical-' + index"
        class="flex items-center gap-2"
      >
        <IpaveScoreLabel :zone="zone" size="detailed" @click="handleZoneClick(zone)" />
        <span class="text-sm text-primary-900">{{ getZoneDesc(zone) }}</span>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { getZoneDesc, IPAVE_ZONES } from "@/utils/ipave"
import { useMapStore } from "@/stores/map"
import IpaveScoreLabel from "@/components/map/score/IpaveScoreLabel.vue"

const mapStore = useMapStore()

const zones = IPAVE_ZONES

const handleZoneClick = (zone: string) => {
  mapStore.toggleAndApplyFilter(zone)
}
</script>
