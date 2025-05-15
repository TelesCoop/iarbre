<script lang="ts" setup>
import type { PlantabilityTile } from "@/types"
import { computed } from "vue"

const props = defineProps({
  data: {
    required: false,
    type: Object as () => PlantabilityTile
  }
})
const landUseData = computed(() => {
  if (!props.data?.details?.top5LandUse) return []
  return Object.entries(props.data.details.top5LandUse).map(([key, value]) => ({
    label: key,
    value: value
  }))
})
</script>

<template>
  <DataTable
    :value="landUseData"
    aria-label="Utilisation des terres - Top 5"
    class="w-full"
    data-key="label"
    responsive-layout="scroll"
    show-gridlines
    size="small"
    striped-rows
  >
    <Column class="w-3/4" field="label" header="Facteur" />
    <Column class="w-1/2" field="value" header="Valeur" sortable />
    <template #empty>
      <div class="flex items-center justify-center w-full h-full">
        <p class="text-sm text-gray-500">Aucune donnée disponible</p>
      </div>
    </template>
  </DataTable>
</template>
