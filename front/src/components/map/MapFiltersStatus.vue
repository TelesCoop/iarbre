<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { computed } from "vue"
import { DataType } from "@/utils/enum"

const mapStore = useMapStore()

const nbFilters = computed(() => {
  return mapStore.filteredValues.length
})

const filterTypeLabel = computed(() => {
  const count = nbFilters.value
  if (count === 0) return ""

  switch (mapStore.selectedDataType) {
    case DataType.PLANTABILITY:
      return count === 1 ? "score" : "scores"
    case DataType.LOCAL_CLIMATE_ZONES:
      return count === 1 ? "zone" : "zones"
    case DataType.VULNERABILITY:
      return count === 1 ? "niveau" : "niveaux"
    default:
      return count === 1 ? "filtre" : "filtres"
  }
})

const filterSummary = computed(() => {
  if (nbFilters.value === 0) return ""
  return `${nbFilters.value} ${filterTypeLabel.value}`
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
    <div
      v-if="mapStore.hasActiveFilters"
      class="filter-status-container"
      data-cy="map-filters-status"
    >
      <div class="filter-status-content">
        <div class="filter-info">
          <span class="filter-count-label">Filtres actifs :</span>
          <span class="filter-summary" data-cy="filter-summary">{{ filterSummary }}</span>
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
.filter-status-container {
  border: 1px solid #059669;
  border-radius: 0.375rem;
  box-shadow:
    0 10px 15px -3px rgb(0 0 0 / 0.1),
    0 4px 6px -4px rgb(0 0 0 / 0.1);
  padding: 0.5rem 1rem;
  margin-top: 0.25rem;
  position: relative;
  z-index: 35;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
}

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

.filter-count-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.filter-summary {
  font-size: 0.875rem;
  font-weight: 600;
  color: #059669;
  background: rgba(5, 150, 105, 0.1);
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
}

@keyframes pulse-subtle {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}
</style>
