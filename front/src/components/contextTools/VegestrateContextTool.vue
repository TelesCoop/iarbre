<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import IconMap from "@/components/icons/IconMap.vue"
import IconBuilding from "@/components/icons/IconBuilding.vue"

const mapStore = useMapStore()
</script>

<template>
  <div class="map-control-panel">
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
</template>
