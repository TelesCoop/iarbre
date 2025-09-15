<script lang="ts" setup>
import { computed } from "vue"
import { type ClimateData } from "@/types/climate"
import { useClimateZone } from "@/composables/useClimateZone"
import ContextDataAccordionItem, {
  type ContextDataFactorGroup
} from "@/components/contextData/ContextDataAccordionItem.vue"

interface ClimateMetricsProps {
  data: ClimateData
  fullHeight?: boolean
}

const props = defineProps<ClimateMetricsProps>()

const categoryWrapperClass = computed(() =>
  props.fullHeight
    ? "space-y-3 pr-2"
    : "max-h-44 xs:max-h-48 sm:max-h-52 md:max-h-56 lg:max-h-56 xl:max-h-100 overflow-y-auto space-y-3 pr-2"
)

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
  <div :class="categoryWrapperClass" role="list">
    <context-data-accordion-item
      v-for="group in climateGroups"
      :key="group.category"
      :group="group"
      color-scheme="climate"
    />
  </div>
</template>
