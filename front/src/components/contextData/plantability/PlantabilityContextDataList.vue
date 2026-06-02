<script lang="ts" setup>
import { type PlantabilityData, PlantabilityImpact } from "@/types/plantability"
import { usePlantabilityData } from "@/composables/usePlantabilityData"
import { toRef, computed } from "vue"
import ContextDataListContainer from "@/components/contextData/shared/ContextDataListContainer.vue"
import type { ContextDataFactorGroup } from "@/types/contextData"
import EmptyMessage from "@/components/EmptyMessage.vue"
import AppButton from "@/components/shared/AppButton.vue"
import PlantabilityDistributionChart from "./PlantabilityDistributionChart.vue"
import { useMapStore } from "@/stores/map"

interface PlantabilityFactorsProps {
  data: PlantabilityData
}

const props = defineProps<PlantabilityFactorsProps>()

const mapStore = useMapStore()

// Land-use detail is only loaded once the map reaches this zoom level;
// below it the backend returns the score distribution over the area.
const LAND_USE_DETAIL_ZOOM = 17
const DISTRIBUTION_ZOOM = 15

const zoomToLandUseDetail = () => mapStore.zoomTo(LAND_USE_DETAIL_ZOOM)
const zoomToDistribution = () => mapStore.zoomTo(DISTRIBUTION_ZOOM)

const { factorGroups, hasFactors } = usePlantabilityData(toRef(props, "data"))

const genericFactorGroups = computed((): ContextDataFactorGroup[] => {
  return factorGroups.value.map((group) => ({
    category: group.category.toString(),
    label: group.label,
    icon: group.icon,
    factors: group.factors.map((factor) => ({
      key: factor.key,
      label: factor.label,
      value: factor.value,
      icon: factor.icon,
      impact:
        factor.impact === PlantabilityImpact.POSITIVE
          ? "positive"
          : factor.impact === PlantabilityImpact.NEGATIVE
            ? "negative"
            : null
    })),
    hasPositiveImpact: group.hasPositiveImpact,
    hasNegativeImpact: group.hasNegativeImpact
  }))
})

const distributionEntries = computed(() => {
  // Check if distribution is directly available (from polygon selection)
  if (props.data?.distribution) {
    return Object.entries(props.data.distribution).map(([score, count]) => ({
      score: Number(score),
      count: count as number
    }))
  }

  // Legacy format: details as string with JSON array of values
  if (!props.data?.details) return []

  let parsed: any
  if (typeof props.data.details === "string") {
    try {
      parsed = JSON.parse(props.data.details)
    } catch {
      return []
    }
  } else {
    parsed = props.data.details
  }

  // Legacy format: JSON array of values
  if (Array.isArray(parsed)) {
    const values: number[] = parsed.filter((value) => typeof value === "number")

    // Count frequency of each unique value
    const frequencyMap = new Map<number, number>()
    values.forEach((value) => {
      frequencyMap.set(value, (frequencyMap.get(value) || 0) + 1)
    })

    return Array.from(frequencyMap.entries()).map(([score, count]) => ({
      score,
      count
    }))
  }

  // For zoom >= 17 it is props.data.top5LandUse.
  return []
})
</script>

<template>
  <div aria-labelledby="factors-section">
    <template v-if="hasFactors">
      <ContextDataListContainer
        :groups="genericFactorGroups"
        aria-label="Liste des paramètres de plantabilité par catégorie"
        color-scheme="plantability"
        variant="cards"
      />
      <div class="zoom-hint" data-cy="zoom-out-hint" role="status">
        <span class="zoom-hint-icon" aria-hidden="true">
          <svg
            fill="none"
            height="12"
            stroke="currentColor"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            viewBox="0 0 24 24"
            width="12"
          >
            <circle cx="11" cy="11" r="7" />
            <line x1="21" x2="16.65" y1="21" y2="16.65" />
            <line x1="8" x2="14" y1="11" y2="11" />
          </svg>
        </span>
        <p class="zoom-hint-text">
          Dézoomez pour voir la distribution des scores de plantabilité sur la zone.
        </p>
        <AppButton
          class="zoom-hint-button"
          data-cy="zoom-out-hint-button"
          size="sm"
          variant="outline"
          @click="zoomToDistribution"
        >
          Dézoomer
        </AppButton>
      </div>
    </template>

    <template v-else>
      <div v-if="distributionEntries.length > 0">
        <PlantabilityDistributionChart :entries="distributionEntries" />
        <div class="zoom-hint" data-cy="zoom-hint" role="status">
          <span class="zoom-hint-icon" aria-hidden="true">
            <svg
              fill="none"
              height="12"
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              viewBox="0 0 24 24"
              width="12"
            >
              <circle cx="11" cy="11" r="7" />
              <line x1="21" x2="16.65" y1="21" y2="16.65" />
              <line x1="11" x2="11" y1="8" y2="14" />
              <line x1="8" x2="14" y1="11" y2="11" />
            </svg>
          </span>
          <p class="zoom-hint-text">
            Zoomez davantage sur la carte pour révéler le détail de l'occupation des sols.
          </p>
          <AppButton
            class="zoom-hint-button"
            data-cy="zoom-hint-button"
            size="sm"
            variant="primary"
            @click="zoomToLandUseDetail"
          >
            Zoomer
          </AppButton>
        </div>
      </div>
      <EmptyMessage
        v-else
        data-cy="empty-message"
        message="Pas de données d'occupation des sols ici."
      />
    </template>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.zoom-hint {
  @apply flex items-center gap-2 mt-2 px-2 py-1.5;
  @apply rounded-md border border-primary-100 bg-primary-50;
}

.zoom-hint-icon {
  @apply flex items-center justify-center shrink-0;
  @apply w-5 h-5 rounded-full bg-white text-primary-500;
}

.zoom-hint-text {
  @apply flex-1 leading-tight text-primary-900;
  @apply text-xs lg:text-sm;
}

.zoom-hint-button {
  @apply shrink-0 px-2 py-0.5 gap-1;
  @apply text-2xs lg:text-xs;
}
</style>
