<script lang="ts" setup>
import MethodologyButton from "@/components/shared/MethodologyButton.vue"
import HourlyRasterSwapButton from "@/components/layerSwitcher/HourlyRasterSwapButton.vue"
import { useMapStore } from "@/stores/map"
import { isHourlyRaster } from "@/utils/hourlyRaster"

interface Props {
  withBorder?: boolean
  showContextTools?: boolean
  showMethodology?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  withBorder: true,
  showContextTools: true,
  showMethodology: true
})

const mapStore = useMapStore()
</script>

<template>
  <div
    :class="['layer-switcher-stack', { 'map-tool-container': props.withBorder }]"
    data-cy="map-layer-switcher"
  >
    <LayerSwitcher />
    <HourlyRasterSwapButton v-if="isHourlyRaster(mapStore.selectedDataType)" />
    <MethodologyButton v-if="props.showMethodology" class="self-center" />
    <MapContextTools v-if="props.showContextTools" />
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.layer-switcher-stack {
  @apply flex flex-col gap-2 w-full;
}
</style>
