<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import IconMap from "@/components/icons/IconMap.vue"
import IconBuilding from "@/components/icons/IconBuilding.vue"
import VegestrateHeightRanges from "@/components/contextTools/VegestrateHeightRanges.vue"

const mapStore = useMapStore()
</script>

<template>
  <div class="map-control-panel border-0">
    <div class="flex items-center gap-1" role="radiogroup" aria-label="Vue végétation">
      <button
        :class="['layer-chip', { active: !mapStore.showVegestrateHeight }]"
        :aria-checked="!mapStore.showVegestrateHeight"
        role="radio"
        type="button"
        @click="mapStore.showVegestrateHeight && mapStore.toggleVegestrateHeight()"
      >
        <IconMap class="layer-chip__icon" :size="14" />
        Strates
      </button>
      <button
        :class="['layer-chip', { active: mapStore.showVegestrateHeight }]"
        :aria-checked="mapStore.showVegestrateHeight"
        role="radio"
        type="button"
        @click="!mapStore.showVegestrateHeight && mapStore.toggleVegestrateHeight()"
      >
        <IconBuilding class="layer-chip__icon" :size="14" />
        Hauteur
      </button>
    </div>
  </div>

  <VegestrateHeightRanges
    v-if="mapStore.showVegestrateHeight"
    class="map-control-panel w-full border-0"
  />
</template>
