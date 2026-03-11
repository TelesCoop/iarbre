<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import VulnerabilityContextTool from "@/components/contextTools/VulnerabilityContextTool.vue"
import { computed } from "vue"

const mapStore = useMapStore()
const show = computed(() => {
  return [DataType.VULNERABILITY, DataType.PLANTABILITY_VULNERABILITY].includes(
    mapStore.selectedDataType
  )
})
</script>

<template>
  <div v-if="show" class="flex flex-wrap items-center gap-2" data-cy="map-context-tools">
    <VulnerabilityContextTool />
    <MapQpvToggleButton />
    <MapCadastreToggleButton />
    <MapBoundaryToggleButton />
  </div>
</template>
