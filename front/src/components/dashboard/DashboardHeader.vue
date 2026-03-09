<script lang="ts" setup>
import { computed } from "vue"
import { RouterLink } from "vue-router"
import AppSelect from "@/components/shared/AppSelect.vue"
import AppBadge from "@/components/shared/AppBadge.vue"
import { useDashboardStore } from "@/stores/dashboard"
import type { DashboardScale } from "@/types/dashboard"

const store = useDashboardStore()

const scaleOptions: { label: string; value: DashboardScale }[] = [
  { label: "Métropole", value: "metropole" },
  { label: "Commune", value: "commune" }
]

const cityOptions = computed(() => store.cities.map((c) => ({ label: c.name, value: c.code })))

const handleScaleChange = (value: string | number) => {
  store.setScale(value as DashboardScale)
}

const handleCityChange = (value: string | number) => {
  store.setCity(value as string)
}

const areaDisplay = computed(() => {
  if (!store.dashboardData) return null
  const ha = store.dashboardData.areaHa
  return ha >= 1000 ? `${(ha / 1000).toFixed(1)} km²` : `${ha} ha`
})

const currentLabel = computed(() => {
  if (store.selectedScale === "commune" && store.selectedCity) {
    return store.selectedCity.name
  }
  return "Métropole de Lyon"
})
</script>

<template>
  <header class="dashboard-header">
    <div class="header-top">
      <div>
        <h1 class="header-title">{{ currentLabel }}</h1>
        <div v-if="store.dashboardData" class="header-badges">
          <AppBadge variant="secondary">{{ areaDisplay }}</AppBadge>
        </div>
      </div>
      <RouterLink :to="{ name: 'map' }" class="back-to-map">
        <svg
          fill="none"
          height="16"
          stroke="currentColor"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          viewBox="0 0 24 24"
          width="16"
          xmlns="http://www.w3.org/2000/svg"
        >
          <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" />
          <line x1="8" x2="8" y1="2" y2="18" />
          <line x1="16" x2="16" y1="6" y2="22" />
        </svg>
        <span>Retourner sur la carte</span>
      </RouterLink>
    </div>

    <div class="header-controls">
      <div class="control-group">
        <label class="control-label">Échelle</label>
        <AppSelect
          :model-value="store.selectedScale"
          :options="scaleOptions"
          placeholder="Échelle"
          @update:model-value="handleScaleChange"
        />
      </div>

      <div v-if="store.selectedScale === 'commune'" class="control-group">
        <label class="control-label">Commune</label>
        <AppSelect
          :model-value="store.selectedCityCode"
          :options="cityOptions"
          placeholder="Choisir une commune..."
          @update:model-value="handleCityChange"
        />
      </div>
    </div>
  </header>
</template>

<style scoped>
@reference "@/styles/main.css";

.dashboard-header {
  @apply relative mb-6 md:mb-8;
  z-index: 10;
}

.header-top {
  @apply flex items-start justify-between mb-4;
}

.back-to-map {
  @apply flex items-center gap-2 text-sm font-medium text-primary-600 bg-primary-50 hover:text-primary-800 transition-colors px-3 py-1.5 rounded-lg hover:bg-primary-100 shrink-0;
}

.header-title {
  @apply text-xl md:text-2xl font-bold text-gray-900;
}

.header-badges {
  @apply flex gap-2 mt-2;
}

.header-controls {
  @apply flex flex-col sm:flex-row gap-3;
}

.control-group {
  @apply flex flex-col gap-1;
  min-width: 200px;
}

.control-label {
  @apply text-xs font-medium text-gray-500 uppercase tracking-wide;
}
</style>
