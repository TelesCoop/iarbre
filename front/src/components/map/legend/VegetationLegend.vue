<script lang="ts" setup>
import { VegetationLegend } from "@/utils/vegetation"
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()

const handleStrateClick = (indice: string) => {
  mapStore.toggleAndApplyFilter(indice)
}
</script>

<template>
  <div class="flex flex-col items-center gap-1 lg:gap-2 font-sans" data-cy="vegetation-legend">
    <div class="legend-header">
      <span class="legend-title">Strate végétale</span>
    </div>

    <div class="strate-list" role="list">
      <button
        v-for="item in VegetationLegend"
        :key="item.indice"
        :aria-label="`${item.label} — cliquez pour filtrer`"
        :aria-pressed="mapStore.isFiltered(item.indice)"
        :class="[
          'strate-item',
          mapStore.isFiltered(item.indice) ? 'is-selected' : '',
          mapStore.hasActiveFilters && !mapStore.isFiltered(item.indice) ? 'is-dimmed' : ''
        ]"
        :data-strate="item.indice"
        :title="item.label"
        role="listitem"
        type="button"
        @click="handleStrateClick(item.indice)"
      >
        <span class="strate-swatch" :style="{ backgroundColor: item.color }"></span>
        <span class="strate-label">{{ item.label }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.strate-list {
  @apply flex w-full max-w-56 flex-col gap-1;
}

.strate-item {
  @apply flex w-full items-center gap-2 cursor-pointer rounded-md px-2 py-1 text-left;
  @apply border-0 bg-transparent;
  @apply transition-colors duration-150 hover:bg-gray-50;
}

.strate-item.is-dimmed {
  @apply opacity-40;
}

.strate-swatch {
  @apply h-4 w-4 shrink-0 rounded-sm border border-gray-300;
}

.strate-item.is-selected .strate-swatch {
  @apply ring-2 ring-gray-600;
}

.strate-label {
  @apply text-xs text-gray-600 lg:text-sm;
}
</style>
