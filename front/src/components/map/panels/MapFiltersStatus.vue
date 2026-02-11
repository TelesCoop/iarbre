<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import IconClose from "@/components/icons/IconClose.vue"
import AppBadge from "@/components/shared/AppBadge.vue"
import MapControlButton from "@/components/map/controls/MapControlButton.vue"

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
    class="map-control-panel flex justify-center items-center gap-2 mb-2"
    data-cy="map-filters-status"
    role="status"
    aria-live="polite"
  >
    <div class="flex items-center gap-2 w-full justify-center">
      <span class="font-medium text-xs">Filtres&nbsp;:</span>

      <AppBadge v-if="filterCount > 0" variant="primary" data-cy="filter-summary">
        {{ filterSummary }}
      </AppBadge>

      <MapControlButton
        aria-label="Supprimer tous les filtres"
        class="w-8 h-8 text-red-500 hover:bg-red-50 hover:border-red-300"
        data-cy="reset-filters-button"
        size="sm"
        @click="handleResetFilters"
      >
        <IconClose :size="14" aria-hidden="true" />
      </MapControlButton>
    </div>
  </div>
</template>
