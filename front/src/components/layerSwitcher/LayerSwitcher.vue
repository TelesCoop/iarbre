<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { RASTER_LAYERS } from "@/utils/rasterLayers"
import AppSelect from "@/components/shared/AppSelect.vue"

const mapStore = useMapStore()

const options = RASTER_LAYERS.map((layer) => ({ label: layer.label, value: layer.key }))
</script>

<template>
  <AppSelect
    :model-value="mapStore.selectedLayer.key"
    :options="options"
    class="w-full"
    data-cy="layer-switcher"
    option-label="label"
    option-value="value"
    placeholder="Sélection de calque"
    @update:model-value="mapStore.setLayer(String($event))"
  />
</template>
