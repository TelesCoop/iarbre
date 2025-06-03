<script lang="ts" setup>
import { type PlantabilityTile } from "@/types/plantability"
import { usePlantabilityFactors } from "@/composables/usePlantabilityFactors"
import PlantabilityContextDataItem from "@/components/contextData/plantability/PlantabilityContextDataItem.vue"
import EmptyMessage from "@/components/EmptyMessage.vue"

interface PlantabilityFactorsProps {
  data: PlantabilityTile
}

const props = defineProps<PlantabilityFactorsProps>()

const { factors, hasFactors } = usePlantabilityFactors(() => props.data)
</script>

<template>
  <section aria-labelledby="factors-section">
    <h3 id="factors-section" class="text-md font-semibold mb-4 flex items-center gap-2">
      <i class="pi pi-chart-bar text-blue-500" aria-hidden="true"></i>
      Paramètres principaux
    </h3>

    <div
      class="h-32 lg:h-40 xl:h-48 overflow-y-auto space-y-3 pr-2 custom-scrollbar"
      role="list"
      aria-label="Liste des paramètres de plantabilité"
    >
      <template v-if="hasFactors">
        <plantability-context-data-item
          v-for="factor in factors"
          :key="factor.key"
          :item="factor"
        />
      </template>

      <template v-else>
        <empty-message message="Aucune donnée disponible" />
      </template>
    </div>
  </section>
</template>

<style scoped></style>
