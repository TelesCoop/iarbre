<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { computed } from "vue"

const mapStore = useMapStore()

const nbFilters = computed(() => {
  return mapStore.filteredValues.length
})

const filterSummary = computed(() => {
  if (nbFilters.value === 0) return ""
  return `${nbFilters.value} ${nbFilters.value === 1 ? "score" : "scores"}`
})
</script>

<template>
  <div v-if="mapStore.hasActiveFilters" class="map-tool-container" data-cy="map-filters-status">
    <div class="flex items-center justify-between gap-3 w-full">
      <div class="flex items-center gap-2 flex-1">
        <span class="font-medium text-xs">Filtres actifs :</span>
        <Chip
          v-if="nbFilters > 0"
          :label="filterSummary"
          class="filter-summary-chip"
          data-cy="filter-summary"
          outlined
          severity="info"
          size="small"
        ></Chip>
      </div>
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
