<script lang="ts" setup>
import { type PlantabilityData } from "@/types/plantability"
import { usePlantabilityData } from "@/composables/usePlantabilityData"
import { toRef } from "vue"
import PlantabilityAccordionItem from "@/components/contextData/plantability/PlantabilityContextDataAccordionItem.vue"
import EmptyMessage from "@/components/EmptyMessage.vue"

interface PlantabilityFactorsProps {
  data: PlantabilityData
}

const props = defineProps<PlantabilityFactorsProps>()

const { factorGroups, hasFactors } = usePlantabilityData(toRef(props, "data"))
</script>

<template>
  <div aria-labelledby="factors-section">
    <h3 id="factors-section" class="text-md font-semibold mb-4 flex items-center gap-2">
      <i aria-hidden="true" class="pi pi-chart-bar text-blue-500"></i>
      Paramètres principaux
    </h3>

    <div
      aria-label="Liste des paramètres de plantabilité par catégorie"
      class="overflow-y-auto space-y-3 pr-2 scrollbar md:max-h-48 lg:max-60"
      role="list"
    >
      <template v-if="hasFactors">
        <plantability-accordion-item
          v-for="group in factorGroups"
          :key="group.category"
          :group="group"
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
