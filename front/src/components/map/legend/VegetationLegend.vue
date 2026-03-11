<script lang="ts" setup>
import { VegetationLegend } from "@/utils/vegetation"
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()

const handleStrateClick = (indice: string) => {
  mapStore.toggleAndApplyFilter(indice)
}
</script>

<template>
  <div
    class="font-accent flex flex-col items-start justify-center text-xs leading-4 gap-2 px-2 py-1"
    data-cy="vegetation-legend"
  >
    <div
      v-for="item in VegetationLegend"
      :key="item.indice"
      class="flex items-center gap-2 cursor-pointer select-none transition-opacity duration-150"
      :class="{ 'opacity-40': mapStore.hasActiveFilters && !mapStore.isFiltered(item.indice) }"
      @click="handleStrateClick(item.indice)"
    >
      <div
        class="w-4 h-4 border border-gray-300 rounded-sm"
        :class="{ 'ring-2 ring-offset-1 ring-gray-600': mapStore.isFiltered(item.indice) }"
        :style="{ backgroundColor: item.color }"
      ></div>
      <span class="text-sm text-primary-900">{{ item.label }}</span>
    </div>
  </div>
</template>
