<script lang="ts" setup>
import { type PlantabilityTile } from "@/types/plantability"
import { usePlantabilityFactors } from "@/composables/usePlantabilityFactors"
import PlantabilityAccordionItem from "@/components/contextData/plantability/PlantabilityContextDataAccordionItem.vue"
import EmptyMessage from "@/components/EmptyMessage.vue"

interface PlantabilityFactorsProps {
  data: PlantabilityTile
}

const props = defineProps<PlantabilityFactorsProps>()

const { factorGroups, hasFactors } = usePlantabilityFactors(() => props.data)
</script>

<template>
  <div aria-labelledby="factors-section">
    <h3 id="factors-section" class="text-md font-semibold mb-4 flex items-center gap-2">
      <i class="pi pi-chart-bar text-blue-500" aria-hidden="true"></i>
      Paramètres principaux
    </h3>

    <div
      class="overflow-y-auto space-y-3 pr-2 custom-scrollbar md:max-h-48 lg:max-60"
      role="list"
      aria-label="Liste des paramètres de plantabilité par catégorie"
    >
      <template v-if="hasFactors">
        <plantability-accordion-item
          v-for="group in factorGroups"
          :key="group.category"
          :group="group"
        />
      </template>

      <template v-else>
        <empty-message message="Aucune donnée connue" data-cy="empty-message" />
      </template>
    </div>
  </div>
</template>

<style scoped></style>
