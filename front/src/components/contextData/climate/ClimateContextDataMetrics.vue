<script lang="ts" setup>
import { computed } from "vue"
import { type ClimateData } from "@/types/climate"
import { useClimateZone } from "@/composables/useClimateZone"
import ContextDataListContainer from "@/components/contextData/shared/ContextDataListContainer.vue"
import type { ContextDataFactorGroup } from "@/types/contextData"

interface ClimateMetricsProps {
  data: ClimateData
  fullHeight?: boolean
}

const props = defineProps<ClimateMetricsProps>()

const {
  climateCategoryToIcon,
  climateCategoryToDescription,
  climateCategoryOrder,
  climateZoneDetailsByCategory,
  climateCategoryKey
} = useClimateZone()

const climateGroups = computed((): ContextDataFactorGroup[] => {
  return climateCategoryOrder.map((category) => {
    const metrics = climateZoneDetailsByCategory[category]
    const factors = metrics.map((metric) => ({
      key: metric.key,
      label: metric.label,
      value: props.data.details?.[metric.key]?.toString() || "N/A",
      icon: "",
      description: metric.description,
      unit: metric.unit
    }))

    return {
      category: climateCategoryKey[category],
      label: category,
      icon: climateCategoryToIcon[category],
      description: climateCategoryToDescription[category],
      factors
    }
  })
})
</script>

<template>
  <context-data-list-container
    :groups="climateGroups"
    color-scheme="climate"
    :full-height="fullHeight"
    :scrollable="true"
    aria-label="Liste des indicateurs climatiques par catégorie"
  />
</template>
