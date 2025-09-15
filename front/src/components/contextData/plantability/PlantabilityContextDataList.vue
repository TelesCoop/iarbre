<script lang="ts" setup>
import { type PlantabilityData, PlantabilityImpact } from "@/types/plantability"
import { usePlantabilityData } from "@/composables/usePlantabilityData"
import { toRef, computed } from "vue"
import ContextDataAccordionItem, {
  type ContextDataFactorGroup
} from "@/components/contextData/shared/ContextDataAccordionItem.vue"
import EmptyMessage from "@/components/EmptyMessage.vue"

interface PlantabilityFactorsProps {
  data: PlantabilityData
}

const props = defineProps<PlantabilityFactorsProps>()

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
</script>

<template>
  <div aria-labelledby="factors-section">
    <h3 id="factors-section" class="text-md font-semibold mb-4 flex items-center gap-2">
      <i aria-hidden="true" class="pi pi-chart-bar text-blue-500"></i>
      Paramètres principaux
    </h3>

    <div
      aria-label="Liste des paramètres de plantabilité par catégorie"
      class="space-y-3 pr-2"
      role="list"
    >
      <template v-if="hasFactors">
        <context-data-accordion-item
          v-for="group in genericFactorGroups"
          :key="group.category"
          :group="group"
          color-scheme="plantability"
        />
      </template>

      <template v-else>
        <empty-message
          data-cy="empty-message"
          message="Pas de données d'occupation des sols ici."
        />
      </template>
    </div>
  </div>
</template>

<style scoped></style>
