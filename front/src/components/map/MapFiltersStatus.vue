<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { computed } from "vue"
import { DataType } from "@/utils/enum"

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
  <Transition
    enter-active-class="transition-all duration-300 ease-out"
    enter-from-class="opacity-0 translate-y-2 scale-95"
    enter-to-class="opacity-100 translate-y-0 scale-100"
    leave-active-class="transition-all duration-200 ease-in"
    leave-from-class="opacity-100 translate-y-0 scale-100"
    leave-to-class="opacity-0 translate-y-2 scale-95"
  >
    <div v-if="mapStore.hasActiveFilters" class="map-tool-container" data-cy="map-filters-status">
      <div class="filter-status-content">
        <div class="filter-info">
          <span class="font-medium text-sm">Filtres actifs :</span>
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
  </Transition>
</template>

<style scoped>
.filter-status-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  width: 100%;
}

.filter-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}
</style>
