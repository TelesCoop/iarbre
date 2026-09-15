<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import IconClose from "@/components/icons/IconClose.vue"
import IconFilter from "@/components/icons/IconFilter.vue"
import AppBadge from "@/components/shared/AppBadge.vue"

const mapStore = useMapStore()

const isVisible = computed(() => mapStore.hasActiveFilters)
const filterCount = computed(() => mapStore.filteredValues.length)

const filterSummary = computed(() => {
  if (filterCount.value === 0) return ""
  const label = filterCount.value === 1 ? "score" : "scores"
  return `${filterCount.value}\u00A0${label}`
})

const handleResetFilters = () => {
  mapStore.resetFilters()
}
</script>

<template>
  <div
    v-if="isVisible"
    class="filters-status"
    data-cy="map-filters-status"
    role="status"
    aria-live="polite"
  >
    <IconFilter class="filters-status__icon" :size="15" aria-hidden="true" />
    <span class="filters-status__label">Filtres</span>

    <AppBadge v-if="filterCount > 0" variant="primary" data-cy="filter-summary">
      {{ filterSummary }}
    </AppBadge>

    <button
      v-tooltip="'Supprimer tous les filtres'"
      class="filters-status__reset"
      type="button"
      data-cy="reset-filters-button"
      aria-label="Supprimer tous les filtres"
      @click="handleResetFilters"
    >
      <IconClose :size="14" aria-hidden="true" />
    </button>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

/* Rendered as a footer row inside the legend panel: a divider separates it from
   the legend content, matching the sibling .legend-attribution footer (pt-1,
   border-gray-100, separation otherwise handled by the panel's own gap). */
.filters-status {
  @apply flex items-center justify-center gap-2 w-full pt-1
         border-t border-gray-100;
}
.filters-status__icon {
  @apply text-primary-500 shrink-0;
}
.filters-status__label {
  @apply text-xs font-semibold text-gray-700 whitespace-nowrap;
}
.filters-status__reset {
  @apply flex items-center justify-center w-6 h-6 rounded-lg shrink-0
         text-gray-400 transition-colors duration-200
         hover:bg-red-50 hover:text-red-600;
}
</style>
