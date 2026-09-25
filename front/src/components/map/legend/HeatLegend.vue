<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { HeatMode, PET_INDEX_LEGEND, SUN_EXPOSURE_LEGEND } from "@/utils/heat"

const mapStore = useMapStore()

const items = computed(() =>
  mapStore.heatMode === HeatMode.PET_INDEX
    ? PET_INDEX_LEGEND.map(({ range, perception, stress, color }) => ({
        key: range,
        label: `${range} - ${perception}`,
        detail: stress,
        color
      }))
    : SUN_EXPOSURE_LEGEND.map(({ range, color }) => ({
        key: range,
        label: range,
        detail: null,
        color
      }))
)
</script>

<template>
  <div
    class="font-accent flex flex-col items-start justify-center text-xs leading-4 gap-2 px-2 py-1"
    data-cy="heat-legend"
  >
    <div v-for="item in items" :key="item.key" class="flex items-center gap-2 select-none">
      <div
        class="w-4 h-4 shrink-0 border border-gray-300 rounded-sm"
        :style="{ backgroundColor: item.color }"
      ></div>
      <span class="text-sm text-primary-900">
        {{ item.label }}
        <span v-if="item.detail" class="text-xs text-gray-500">({{ item.detail }})</span>
      </span>
    </div>
  </div>
</template>
