<script lang="ts" setup>
import { computed } from "vue"
import AppSpinner from "@/components/shared/AppSpinner.vue"
import NarrativeSection from "@/components/dashboard/NarrativeSection.vue"
import PlantabilityWidget from "@/components/dashboard/widgets/PlantabilityWidget.vue"
import HeatWidget from "@/components/dashboard/widgets/HeatWidget.vue"
import SurfaceTypeWidget from "@/components/dashboard/widgets/SurfaceTypeWidget.vue"
import VegetationSurfaceWidget from "@/components/dashboard/widgets/VegetationSurfaceWidget.vue"
import BuildingCharacteristicsWidget from "@/components/dashboard/widgets/BuildingCharacteristicsWidget.vue"
import { useDashboardStore } from "@/stores/dashboard"

const store = useDashboardStore()

const hasData = computed(() => store.dashboardData !== null && !store.loading)
</script>

<template>
  <div v-if="store.loading" class="narrative-loading">
    <AppSpinner size="lg" color="#426A45" />
    <p class="loading-text">Chargement des données...</p>
  </div>

  <div v-else-if="store.error" class="narrative-error">
    <p class="error-text">{{ store.error }}</p>
  </div>

  <div v-else-if="hasData" class="dashboard-narrative">
    <NarrativeSection
      title="Potentiel de végétalisation"
      question="Combien de surfaces sont disponibles immédiatement pour planter des strates hautes ?"
    >
      <PlantabilityWidget :data="store.dashboardData!.plantability" />
    </NarrativeSection>

    <NarrativeSection
      title="Inventaire stratifié de végétation"
      question="Quelle est la place de la végétation aujourd'hui ?"
    >
      <VegetationSurfaceWidget :data="store.dashboardData!.vegetation" />
    </NarrativeSection>

    <NarrativeSection
      title="Contraintes du territoire"
      question="Quelles sont les contraintes bloquantes ?"
    >
      <BuildingCharacteristicsWidget
        :lcz="store.dashboardData!.lcz"
        :buildings="store.dashboardData!.buildings"
      />
      <SurfaceTypeWidget :data="store.dashboardData!.lcz" />
    </NarrativeSection>

    <NarrativeSection
      title="Risques et vulnérabilités"
      question="À quels risques climatiques le territoire est-il exposé ?"
    >
      <HeatWidget :data="store.dashboardData!.vulnerability" />
    </NarrativeSection>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.dashboard-narrative {
  @apply flex flex-col gap-10;
}

.narrative-loading {
  @apply flex flex-col items-center justify-center py-20 gap-4;
}

.loading-text {
  @apply text-sm text-gray-500;
}

.narrative-error {
  @apply flex items-center justify-center py-20;
}

.error-text {
  @apply text-sm text-red-500;
}
</style>
