<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import VulnerabilityContextTool from "@/components/contextTools/VulnerabilityContextTool.vue"
import VegestrateContextTool from "@/components/contextTools/VegestrateContextTool.vue"
import PetContextTool from "@/components/contextTools/PetContextTool.vue"
import { computed } from "vue"

const mapStore = useMapStore()
const show = computed(() => {
  return [
    DataType.VULNERABILITY,
    DataType.PLANTABILITY_VULNERABILITY,
    DataType.VEGESTRATE,
    DataType.PET
  ].includes(mapStore.selectedDataType)
})
</script>

<template>
  <div
    v-if="show"
    class="flex w-full flex-wrap items-center justify-center gap-2"
    data-cy="map-context-tools"
  >
    <VulnerabilityContextTool
      v-if="
        [DataType.VULNERABILITY, DataType.PLANTABILITY_VULNERABILITY].includes(
          mapStore.selectedDataType
        )
      "
    />
    <VegestrateContextTool v-if="mapStore.selectedDataType === DataType.VEGESTRATE" />
    <PetContextTool v-if="mapStore.selectedDataType === DataType.PET" />
  </div>
</template>
