<script lang="ts" setup>
import { BiosphereIntegrityLegend } from "@/utils/biosphere_functional_integrity"
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()

const handleClick = (name: string) => {
  mapStore.toggleAndApplyFilter(name)
}
</script>

<template>
  <div
    class="font-accent flex flex-col items-start justify-center text-xs leading-4 gap-2 px-2 py-1"
    data-cy="biosphere-integrity-legend"
  >
    <div
      v-for="(color, name, index) in BiosphereIntegrityLegend"
      :key="index"
      class="flex items-center gap-2 cursor-pointer select-none transition-opacity duration-150"
      :class="{ 'opacity-40': mapStore.hasActiveFilters && !mapStore.isFiltered(name) }"
      @click="handleClick(name)"
    >
      <div
        class="w-4 h-4 border border-gray-300 rounded-sm"
        :class="{ 'ring-2 ring-offset-1 ring-gray-600': mapStore.isFiltered(name) }"
        :style="{ backgroundColor: color }"
      ></div>
      <span class="text-sm text-primary-900">{{ name }}</span>
    </div>
  </div>
</template>
