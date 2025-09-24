<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { computed } from "vue"

const mapStore = useMapStore()

const nbFilters = computed(() => {
  return mapStore.filteredValues.length
})

const filterSummary = computed(() => {
  if (nbFilters.value === 0) return ""
  return `${nbFilters.value}\u00A0${nbFilters.value === 1 ? "score" : "scores"}`
})
</script>

<template>
  <div
    v-if="mapStore.hasActiveFilters"
    class="bg-white flex px-4 py-2 justify-center items-center gap-2 rounded-lg mb-2"
    data-cy="map-filters-status"
  >
    <div class="flex items-center gap-2 w-full justify-center">
      <span class="font-medium text-xs">Filtres&nbsp;:</span>
      <Chip
        v-if="nbFilters > 0"
        :label="filterSummary"
        class="filter-summary-chip"
        data-cy="filter-summary"
        outlined
        severity="info"
        size="small"
      ></Chip>
      <Button
        :icon-class="'filter-reset-icon'"
        data-cy="reset-filters-button"
        icon="pi pi-times"
        label="Effacer"
        outlined
        severity="danger"
        size="small"
        title="Supprimer tous les filtres"
        @click="mapStore.resetFilters()"
      >
      </Button>
    </div>
  </div>
</template>
