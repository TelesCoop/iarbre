<script lang="ts" setup>
import type { PlantabilityTile } from "@/types"
import { computed } from "vue"

const props = defineProps({
  data: {
    required: true,
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
    empty-message="Aucune donnée disponible"
    responsive-layout="scroll"
    show-gridlines
    size="small"
    striped-rows
  >
    <Column class="w-3/4" field="label" header="Type d'utilisation" />
    <Column class="w-1/2" field="value" header="Valeur" sortable />
  </DataTable>
</template>
