<script lang="ts" setup>
import { watch } from "vue"
import { useMapStore } from "@/stores/map"
import { useFloraRecommendations } from "@/composables/useFloraRecommendations"
import type { PlantabilityData } from "@/types/plantability"
import FloraLocalSummary from "./FloraLocalSummary.vue"
import FloraSpeciesList from "./FloraSpeciesList.vue"

const mapStore = useMapStore()
const { recommendations, loading, error, fetchRecommendations } = useFloraRecommendations()

watch(
  () => mapStore.clickCoordinates,
  (coords) => {
    if (coords) {
      const contextData = mapStore.contextData.data as PlantabilityData | null
      const plantabilityScore = contextData?.plantabilityNormalizedIndice
      fetchRecommendations(coords.lat, coords.lng, plantabilityScore)
    }
  },
  { immediate: true }
)
</script>

<template>
  <div class="flora-panel">
    <!-- Loading -->
    <div v-if="loading" class="skeleton-container">
      <div class="skeleton skeleton-summary" />
      <div class="skeleton skeleton-card" />
      <div class="skeleton skeleton-card" />
      <div class="skeleton skeleton-card" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>

    <!-- Empty -->
    <div v-else-if="!recommendations" class="empty-message">
      <p>Cliquez sur la carte pour obtenir des recommandations d'arbres.</p>
    </div>

    <!-- Results -->
    <template v-else>
      <FloraLocalSummary
        :summary="recommendations.localFloraSummary"
        :lcz-context="recommendations.lczContext"
      />
      <div v-if="recommendations.recommendations.length > 0" class="recommendations-section">
        <h3 class="section-title">Arbres recommandés</h3>
        <FloraSpeciesList :recommendations="recommendations.recommendations" />
      </div>
      <div v-else class="empty-message">
        <p>Aucune recommandation disponible pour ce contexte.</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.flora-panel {
  @apply flex flex-col gap-3;
}

.skeleton-container {
  @apply flex flex-col gap-2;
}

.skeleton {
  @apply bg-gray-200 rounded-lg animate-pulse;
}

.skeleton-summary {
  @apply h-24;
}

.skeleton-card {
  @apply h-20;
}

.error-message {
  @apply p-3 text-sm text-red-600 bg-red-50 rounded-lg;
}

.error-message p {
  @apply mb-0;
}

.empty-message {
  @apply p-3 text-sm text-gray-500;
}

.empty-message p {
  @apply mb-0;
}

.recommendations-section {
  @apply flex flex-col gap-2;
}

.section-title {
  @apply text-sm font-semibold text-gray-700 mb-0;
}
</style>
