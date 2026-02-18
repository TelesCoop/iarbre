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
  <div class="flex items-center gap-2" data-cy="map-context-tools">
    <MapQpvToggleButton />
    <MapCadastreToggleButton />
    <VulnerabilityContextTool v-if="show" />
  </div>
</template>
