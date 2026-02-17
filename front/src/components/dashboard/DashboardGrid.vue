<script lang="ts" setup>
import { computed } from "vue"
import AppSpinner from "@/components/shared/AppSpinner.vue"
import PlantabilityWidget from "@/components/dashboard/widgets/PlantabilityWidget.vue"
import HeatWidget from "@/components/dashboard/widgets/HeatWidget.vue"
import VegetationWidget from "@/components/dashboard/widgets/VegetationWidget.vue"
import BuildingWidget from "@/components/dashboard/widgets/BuildingWidget.vue"
import SurfaceTypeWidget from "@/components/dashboard/widgets/SurfaceTypeWidget.vue"
import VegetationWaterWidget from "@/components/dashboard/widgets/VegetationWaterWidget.vue"
import { useDashboardStore } from "@/stores/dashboard"

const store = useDashboardStore()

const hasData = computed(() => store.dashboardData !== null && !store.loading)
</script>

<template>
  <div v-if="store.loading" class="grid-loading">
    <AppSpinner size="lg" color="#426A45" />
    <p class="loading-text">Chargement des données...</p>
  </div>

  <div v-else-if="store.error" class="grid-error">
    <p class="error-text">{{ store.error }}</p>
  </div>

  <div v-else-if="hasData" class="dashboard-grid">
    <PlantabilityWidget :data="store.dashboardData!.plantability" />
    <HeatWidget :data="store.dashboardData!.vulnerability" />
    <VegetationWidget :data="store.dashboardData!.vegetation" />
    <BuildingWidget :data="store.dashboardData!.lcz" />
    <SurfaceTypeWidget :data="store.dashboardData!.lcz" />
    <VegetationWaterWidget :data="store.dashboardData!.lcz" />
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.dashboard-grid {
  @apply grid gap-4 md:gap-6;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1280px) {
  .dashboard-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.grid-loading {
  @apply flex flex-col items-center justify-center py-20 gap-4;
}

.loading-text {
  @apply text-sm text-gray-500;
}

.grid-error {
  @apply flex items-center justify-center py-20;
}

.error-text {
  @apply text-sm text-red-500;
}
</style>
