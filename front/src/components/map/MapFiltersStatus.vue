<script lang="ts" setup>
import { useMapStore } from "@/stores/map"

const mapStore = useMapStore()

const handleResetFilters = () => {
  mapStore.clearAllFilters()
}
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
        <div class="filter-status-info">
          <span class="filter-status-icon">🔍</span>
          <div class="filter-status-text">
            <span class="filter-status-title">Filtres actifs</span>
            <span class="filter-status-summary">{{ mapStore.getFilterSummary }}</span>
          </div>
        </div>

        <button
          class="filter-reset-button"
          data-cy="reset-filters-button"
          title="Supprimer tous les filtres"
          @click="handleResetFilters"
        >
          <span class="filter-reset-icon">✕</span>
          <span class="filter-reset-text">Reset</span>
        </button>
      </div>

      <div class="filter-status-indicator">
        <span class="filter-count-badge">{{ mapStore.getActiveFiltersCount }}</span>
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
}

.filter-status-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.filter-status-icon {
  font-size: 1.125rem;
  filter: grayscale(0.2);
}

.filter-status-text {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.filter-status-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #047857;
  font-family: inherit;
}

.filter-status-summary {
  font-size: 0.75rem;
  color: #059669;
}

.filter-reset-button {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.625rem;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.375rem;
  transition: all 0.2s;
  color: #b91c1c;
  cursor: pointer;
}

.filter-reset-button:hover {
  background-color: #fee2e2;
  color: #991b1b;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
}

.filter-reset-button:focus {
  outline: none;
  box-shadow:
    0 0 0 2px #fca5a5,
    0 0 0 4px #ffffff;
}

.filter-reset-icon {
  font-size: 0.875rem;
  font-weight: 700;
}

.filter-reset-text {
  font-size: 0.75rem;
  font-weight: 500;
  font-family: inherit;
}

.filter-status-indicator {
  position: absolute;
  top: -0.25rem;
  right: -0.25rem;
}

.filter-count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  background-color: #047857;
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  border-radius: 9999px;
  border: 2px solid white;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  animation: pulse-subtle 2s ease-in-out infinite;
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
