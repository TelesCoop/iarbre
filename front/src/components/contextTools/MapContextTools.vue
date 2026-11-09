<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import VulnerabilityContextTool from "@/components/contextTools/VulnerabilityContextTool.vue"
import VegestrateContextTool from "@/components/contextTools/VegestrateContextTool.vue"
import HourlyRasterContextTool from "@/components/contextTools/HourlyRasterContextTool.vue"
import { isHourlyRaster } from "@/utils/hourlyRaster"
import { computed } from "vue"

const mapStore = useMapStore()
const show = computed(() => {
  return (
    [DataType.VULNERABILITY, DataType.PLANTABILITY_VULNERABILITY, DataType.VEGESTRATE].includes(
      mapStore.selectedDataType
    ) || isHourlyRaster(mapStore.selectedDataType)
  )
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
    <HourlyRasterContextTool v-if="isHourlyRaster(mapStore.selectedDataType)" />
  </div>
</template>
